import nacl from 'tweetnacl';

type Json = Record<string, unknown>;

type GatewayEvent = {
	type: 'event';
	event: string;
	seq?: number;
	payload?: any;
};

type GatewayResponse = {
	type: 'res';
	id: string;
	ok: boolean;
	payload?: any;
	error?: {
		code?: string;
		message?: string;
		details?: any;
		retryable?: boolean;
		retryAfterMs?: number;
	};
};

type PendingRequest = {
	resolve: (value: any) => void;
	reject: (error: Error) => void;
};

type DeviceIdentity = {
	version: 1;
	deviceId: string;
	publicKey: string;
	privateKey: string;
	createdAtMs: number;
};

type OpenClawWsClientOptions = {
	url: string;
	token: string;
	agentId?: string;
	clientId?: string;
	clientVersion?: string;
	platform?: string;
	mode?: string;
	storageKey?: string;
	scopes?: string[];
	onEvent?: (event: GatewayEvent) => void;
};

function base64urlEncode(buf: Uint8Array): string {
	let s = '';
	for (const b of buf) s += String.fromCharCode(b);
	return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

function base64urlDecode(s: string): Uint8Array {
	const normalized = s.replace(/-/g, '+').replace(/_/g, '/');
	const padded = normalized + '='.repeat((4 - (normalized.length % 4 || 4)) % 4);
	const raw = atob(padded);
	const out = new Uint8Array(raw.length);
	for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
	return out;
}

async function sha256Hex(data: Uint8Array): Promise<string> {
	const digest = await crypto.subtle.digest('SHA-256', data.buffer as ArrayBuffer);
	return Array.from(new Uint8Array(digest))
		.map((b) => b.toString(16).padStart(2, '0'))
		.join('');
}

async function createIdentity(): Promise<DeviceIdentity> {
	const seed = crypto.getRandomValues(new Uint8Array(32));
	const kp = nacl.sign.keyPair.fromSeed(seed);
	const deviceId = await sha256Hex(kp.publicKey);

	return {
		version: 1,
		deviceId,
		publicKey: base64urlEncode(kp.publicKey),
		privateKey: base64urlEncode(seed),
		createdAtMs: Date.now(),
	};
}

async function loadOrCreateIdentity(storageKey: string): Promise<DeviceIdentity> {
	const raw = localStorage.getItem(storageKey);
	if (raw) {
		const parsed = JSON.parse(raw) as DeviceIdentity;
		return parsed;
	}

	const identity = await createIdentity();
	localStorage.setItem(storageKey, JSON.stringify(identity));
	return identity;
}

function buildDeviceSignaturePayload(params: {
	deviceId: string;
	clientId: string;
	clientMode: string;
	role: string;
	scopes: string[];
	signedAtMs: number;
	token?: string;
	nonce: string;
}) {
	return [
		'v2',
		params.deviceId,
		params.clientId,
		params.clientMode,
		params.role,
		params.scopes.join(','),
		String(params.signedAtMs),
		params.token ?? '',
		params.nonce,
	].join('|');
}

function signPayload(privateKeySeedBase64Url: string, payload: string): string {
	const seed = base64urlDecode(privateKeySeedBase64Url);
	const kp = nacl.sign.keyPair.fromSeed(seed);
	const sig = nacl.sign.detached(new TextEncoder().encode(payload), kp.secretKey);
	return base64urlEncode(sig);
}

function makeId() {
	return crypto.randomUUID();
}

export class OpenClawWsClient {
	private ws?: WebSocket;
	private pending = new Map<string, PendingRequest>();
	private connectNonce?: string;
	private connected = false;
	private connectPromise?: Promise<void>;
	private identity?: DeviceIdentity;
	private eventHandlers: Map<string, (event: GatewayEvent) => void> = new Map();
	private messageHandler?: (runId: string, text: string) => void;
	private toolCallHandler?: (event: {
		toolCallId: string;
		name: string;
		title?: string;
		phase: 'start' | 'update' | 'end';
		status?: string;
	}) => void;
	private lastRunId = '';

	private readonly opts: Required<Omit<OpenClawWsClientOptions, 'onEvent'>> & {
		onEvent?: (event: GatewayEvent) => void;
	};

	constructor(opts: OpenClawWsClientOptions) {
		this.opts = {
			url: opts.url,
			token: opts.token,
			agentId: opts.agentId ?? 'main',
			clientId: opts.clientId ?? 'cli',
			clientVersion: opts.clientVersion ?? '0.1.0',
			platform: opts.platform ?? 'web',
			mode: opts.mode ?? 'webchat',
			storageKey: opts.storageKey ?? 'openclaw.device.identity.v1',
			scopes: opts.scopes ?? [
				'operator.read',
				'operator.write',
				'operator.approvals',
				'operator.pairing',
			],
			onEvent: opts.onEvent,
		};
	}

	async connect(): Promise<void> {
		if (this.connected) return;
		if (this.connectPromise) return this.connectPromise;

		this.connectPromise = (async () => {
			this.identity = await loadOrCreateIdentity(this.opts.storageKey);

			await new Promise<void>((resolve, reject) => {
				const ws = new WebSocket(this.opts.url);
				this.ws = ws;

				const onOpen = () => {
					// ждём connect.challenge
				};

				const onError = () => {
					reject(new Error('WebSocket connection failed'));
				};

				const onClose = (ev: CloseEvent) => {
					if (!this.connected) {
						reject(new Error(`Gateway closed during connect: ${ev.code} ${ev.reason}`));
					}
				};

				const onMessage = async (ev: MessageEvent) => {
					const msg = JSON.parse(String(ev.data)) as GatewayEvent | GatewayResponse;

					if (msg.type === 'event' && msg.event === 'connect.challenge') {
						this.connectNonce = String(msg.payload?.nonce ?? '');

						try {
							await this.sendConnect();
							this.connected = true;
							resolve();
						} catch (err) {
							reject(err);
						} finally {
							this.connected = true;
						}
						return;
					}

					this.handleMessage(msg);
				};

				ws.addEventListener('open', onOpen);
				ws.addEventListener('error', onError);
				ws.addEventListener('close', onClose);
				ws.addEventListener('message', onMessage);
			});

			this.ws?.addEventListener('message', (ev) => {
				const msg = JSON.parse(String(ev.data)) as GatewayEvent | GatewayResponse;
				this.handleMessage(msg);
			});

			this.ws?.addEventListener('close', () => {
				this.connected = false;
			});
		})();

		try {
			await this.connectPromise;
		} finally {
			this.connectPromise = undefined;
		}
	}

	disconnect() {
		this.ws?.close();
		this.connected = false;
	}

	async request<T = any>(method: string, params: Json = {}): Promise<T> {
		if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
			throw new Error('WebSocket is not connected');
		}

		const id = makeId();
		const frame = {
			type: 'req',
			id,
			method,
			params,
		};

		return new Promise<T>((resolve, reject) => {
			this.pending.set(id, { resolve, reject });
			this.ws!.send(JSON.stringify(frame));
		});
	}

	private async sendConnect() {
		if (!this.identity) throw new Error('Device identity is not initialized');
		if (!this.connectNonce) throw new Error('Missing connect nonce');

		const signedAt = Date.now();
		const payload = buildDeviceSignaturePayload({
			deviceId: this.identity.deviceId,
			clientId: this.opts.clientId,
			clientMode: this.opts.mode,
			role: 'operator',
			scopes: this.opts.scopes,
			signedAtMs: signedAt,
			token: this.opts.token,
			nonce: this.connectNonce,
		});

		const signature = signPayload(this.identity.privateKey, payload);

		return this.request('connect', {
			minProtocol: 3,
			maxProtocol: 3,
			client: {
				id: this.opts.clientId,
				version: this.opts.clientVersion,
				platform: this.opts.platform,
				mode: this.opts.mode,
			},
			role: 'operator',
			scopes: this.opts.scopes,
			caps: ['tool-events'],
			commands: [],
			permissions: {},
			auth: {
				token: this.opts.token,
			},
			locale: navigator.language || 'ru-RU',
			userAgent: navigator.userAgent,
			device: {
				id: this.identity.deviceId,
				publicKey: this.identity.publicKey,
				signature,
				signedAt,
				nonce: this.connectNonce,
			},
		});
	}

	private handleMessage(msg: GatewayEvent | GatewayResponse) {
		if (msg.type === 'event') {
			const event = msg;

			const isAgentOrChat = event.event === 'agent' || event.event === 'chat';
			const hasOurSessionKey = msg?.payload?.sessionKey === 'agent:api:main';
			const payload = event.payload as {
				runId?: string;
				stream?: string;
				data?: {
					delta?: string;
					text?: string;
					phase?: string;
					name?: string;
					toolCallId?: string;
					title?: string;
					status?: string;
				};
			};

			if (this.messageHandler || this.toolCallHandler) {
				const runId = payload?.runId ?? '';
				const jsonText = payload?.data?.text ?? '';

				// Tool call lifecycle (kind: "tool" or "command" come through stream "item")
				if (
					isAgentOrChat &&
					(payload.stream === 'item' || payload.stream === 'tool') &&
					payload.data?.name &&
					payload.data?.toolCallId
				) {
					const phase = payload.data.phase as 'start' | 'update' | 'end' | undefined;
					if (phase === 'start' || phase === 'update' || phase === 'end') {
						this.toolCallHandler?.({
							toolCallId: payload.data.toolCallId,
							name: payload.data.name,
							title: payload.data.title,
							phase,
							status: payload.data.status,
						});
					}
				}

				// If we have our sessionKey, save runId and process
				if (isAgentOrChat && hasOurSessionKey && runId) {
					this.lastRunId = runId;
					if (jsonText) {
						this.messageHandler?.(runId, jsonText);
					}
				}
				// If no our sessionKey but we have lastRunId, use existing (don't overwrite)
				else if (isAgentOrChat && !hasOurSessionKey && this.lastRunId === runId && jsonText) {
					this.messageHandler?.(this.lastRunId, jsonText);
				}
			}

			this.eventHandlers.forEach((handler) => handler(event));
			this.opts.onEvent?.(event);
			return;
		}

		const pending = this.pending.get(msg.id);
		if (!pending) return;

		this.pending.delete(msg.id);

		if (msg.ok) {
			pending.resolve(msg.payload);
		} else {
			pending.reject(
				new Error(
					`[${msg.error?.code ?? 'GATEWAY_ERROR'}] ${msg.error?.message ?? 'Request failed'}`
				)
			);
		}
	}

	async ask(
		message: string,
		opts?: { agentId?: string; provider?: string; model?: string }
	): Promise<void> {
		await this.request('agent', {
			agentId: opts?.agentId ?? this.opts.agentId,
			message,
			provider: opts?.provider,
			model: opts?.model,
			idempotencyKey: makeId(),
		});
	}

	onEvent(handler: (event: GatewayEvent) => void) {
		this.eventHandlers.set('_global', handler);
		this.opts.onEvent = handler;
	}

	onMessage(handler: (runId: string, text: string) => void) {
		this.messageHandler = handler;
	}

	onToolCall(handler: (event: { toolCallId: string; name: string; title?: string; phase: 'start' | 'update' | 'end'; status?: string }) => void) {
		this.toolCallHandler = handler;
	}
}

const baseUrl = import.meta.env.VITE_OPENCLAW_BASE_URL || 'http://localhost:8080';
const apiKey = import.meta.env.VITE_OPENCLAW_API_KEY || '';

export const wsClient = new OpenClawWsClient({
	url: baseUrl,
	token: apiKey,
	agentId: 'api',
});
