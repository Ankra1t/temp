from html2image import Html2Image

from .CalculationService import CalculationService
from models import Calculation


class HTIService:
    def __init__(self, calcService: CalculationService) -> None:
        self.path = '_calc_images'
        self.hti = Html2Image(
            output_path=self.path,
            custom_flags=[
                '--headless',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--disable-plugins',
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
            ]
        )
        self.calcService = calcService

    def create_calculation_image(self, user_id: int, calc: Calculation):
        """Возвращает ссылку на картинку и подпись"""
        width = 1280
        height = 1280

        is_saved = calc.in_stat
        if not is_saved:
            len_tp = len(calc.tp_ratio)
            if len_tp > 1:
                height += 70 * (len_tp - 1)
            if len_tp > 2:
                height += 70 * (len_tp // 2 - 1)
        else:
            height += 100

        html_value, caption = self.calcService.html_calculation(user_id, calc)

        file_name = f'{user_id}.png'
        self.hti.screenshot(
            save_as=file_name,
            size=(width, height),
            html_str=f"""
            	<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
				<link rel="stylesheet" href="style.css" />
				<div class="container">
					<div class="main">
						<div class="bg">
							<svg
								width="1276"
								height="402"
								viewBox="0 0 1276 402"
								fill="none"
								xmlns="http://www.w3.org/2000/svg">
								<path
									d="M0 245.235C0 193.442 15.0862 154.274 45.2586 127.732C75.431 101.191 118.159 87.9197 173.443 87.9197C225.612 87.9197 266.198 96.0297 295.203 112.25C324.207 128.47 338.709 152.431 338.709 184.134C338.709 189.11 336.957 193.165 333.454 196.299C330.144 199.432 325.862 200.999 320.606 200.999H277.099C263.862 200.999 252.669 194.271 243.52 180.816C232.035 163.49 211.109 154.827 180.742 154.827C152.906 154.827 133.148 161.923 121.468 176.116C109.983 190.124 104.241 213.164 104.241 245.235C104.241 276.938 110.178 299.885 122.052 314.078C134.121 328.27 154.658 335.367 183.662 335.367C214.029 335.367 234.955 326.704 246.44 309.378C255.589 295.738 266.782 288.918 280.019 288.918H323.526C328.782 288.918 333.064 290.577 336.373 293.895C339.877 297.028 341.629 300.991 341.629 305.784C341.629 337.486 327.127 361.448 298.123 377.668C269.313 393.888 228.823 401.998 176.654 401.998C119.619 401.998 75.9176 388.727 45.5506 362.185C15.1835 335.643 0 296.66 0 245.235Z"
									fill="#F7F7F7" />
								<path
									d="M409.955 376.562C384.26 359.604 371.412 335.643 371.412 304.678C371.412 273.712 384.26 249.935 409.955 233.347C435.845 216.758 469.132 208.464 509.816 208.464H606.465C606.465 186.898 601.696 171.877 592.157 163.398C582.619 154.919 567.533 150.68 546.899 150.68C519.841 150.68 500.862 156.947 489.961 169.48C481.59 179.249 470.397 184.134 456.382 184.134H412.875C407.619 184.134 403.239 182.567 399.735 179.434C396.426 176.116 394.772 172.061 394.772 167.269C394.772 114.369 447.817 87.9197 553.907 87.9197C600.236 87.9197 637.416 97.7807 665.447 117.503C693.478 137.04 707.494 167.361 707.494 208.464V379.603C707.494 384.58 705.839 388.635 702.53 391.768C699.221 394.901 694.938 396.468 689.682 396.468H633.328C628.072 396.468 623.79 394.901 620.481 391.768C617.171 388.45 615.517 384.395 615.517 379.603V371.032C584.76 391.86 549.527 402.182 509.816 401.998C469.132 401.998 435.845 393.519 409.955 376.562ZM472.733 304.678C472.733 314.815 476.821 323.109 484.997 329.561C493.173 336.012 504.755 339.237 519.744 339.237C549.721 339.237 578.629 330.943 606.465 314.354V271.224H516.824C503.198 271.224 492.394 274.357 484.413 280.624C476.626 286.891 472.733 294.909 472.733 304.678Z"
									fill="#F7F7F7" />
								<path
									d="M779.616 379.603V17.1416C779.616 12.165 781.27 8.10999 784.579 4.97659C788.083 1.65886 792.366 0 797.427 0H862.833C868.089 0 872.371 1.65886 875.68 4.97659C878.99 8.10999 880.644 12.165 880.644 17.1416V379.603C880.644 384.58 878.892 388.635 875.389 391.768C872.079 394.901 867.894 396.468 862.833 396.468H797.427C792.171 396.468 787.889 394.901 784.579 391.768C781.27 388.635 779.616 384.58 779.616 379.603Z"
									fill="#F7F7F7" />
								<path
									d="M934.371 245.235C934.371 193.442 949.457 154.274 979.629 127.732C1009.8 101.191 1052.53 87.9197 1107.81 87.9197C1159.98 87.9197 1200.57 96.0297 1229.57 112.25C1258.58 128.47 1273.08 152.431 1273.08 184.134C1273.08 189.11 1271.33 193.165 1267.82 196.299C1264.52 199.432 1260.23 200.999 1254.98 200.999H1211.47C1198.23 200.999 1187.04 194.271 1177.89 180.816C1166.41 163.49 1145.48 154.827 1115.11 154.827C1087.28 154.827 1067.52 161.923 1055.84 176.116C1044.35 190.124 1038.61 213.164 1038.61 245.235C1038.61 276.938 1044.55 299.885 1056.42 314.078C1068.49 328.27 1089.03 335.367 1118.03 335.367C1148.4 335.367 1169.33 326.704 1180.81 309.378C1189.96 295.738 1201.15 288.918 1214.39 288.918H1257.9C1263.15 288.918 1267.43 290.577 1270.74 293.895C1274.25 297.028 1276 300.991 1276 305.784C1276 337.486 1261.5 361.448 1232.49 377.668C1203.68 393.888 1163.19 401.998 1111.03 401.998C1053.99 401.998 1010.29 388.727 979.921 362.185C949.554 335.643 934.371 296.66 934.371 245.235Z"
									fill="#F7F7F7" />
							</svg>
						</div>
         				{html_value}
          			</div>
				</div>
    		""",
            css_str=css_template + f"""
				.main {{
					width: {width}px;
				}}
			""",
        )

        return f'{self.path}/{file_name}', caption


css_template = """body,
.container {
	font-family: 'Montserrat';

	font-size: 50px;
	line-height: 1.4;
	font-weight: 500;
 	overflow: hidden;
}

.main {
	padding: 70px;
	margin: 0 auto;
	width: 1280px;
	color: #131313;

	display: flex;
	flex-direction: column;
	gap: 30px;

	position: relative;
}

.bg {
	position: absolute;
	z-index: -1;
	top: 50%;
	left: 0;
	width: 100%;

	transform: translateY(-50%);
}

.bg svg {
	width: 100%;
}

.header {
	display: flex;
	align-items: center;
	font-weight: 700;
	font-size: 70px;
	margin-bottom: 30px;
}


.header_name {
	display: flex;
	align-items: center;
	gap: 12px;
	white-space: nowrap;
}

.title {
	color: #0094fe;
}

.title.long {
	color: #0a8754;
}

.title.short {
	color: #dd1c1a;
}

.name {
	flex: 0 0 460px;
}

.value {
	flex: 1 1 auto;
	font-weight: 600;
	color: #0094fe;
}

.content {
	border-radius: 20px;
	border: 1px solid rgba(0, 148, 254, 0.3);
	padding: 0 40px;
}

.major {
	background: #0094fe;
	color: white;
}

.major .value {
	color: white;
}

.block {
	display: flex;
	justify-content: space-between;
	padding: 40px 0;

	position: relative;
}

.block::before {
	content: "";
	position: absolute;
	top: 100%;

	height: 1px;
	width: 100%;
	background: rgba(0, 148, 254, 0.3);
}

.major .block::before {
	background: rgba(255, 255, 255, 0.3);
}

.block:last-child::before {
	display: none;
}

.profit {
	flex: 1 1 auto;
	display: grid;
	grid-template-columns: 1fr 1fr;
	align-items: center;
	gap: 15px 30px;
	flex-wrap: wrap;
}

.profit span {
	flex: 0 0 49%;
}

.profit span:nth-child(2n) {
	position: relative;
}

.profit span:nth-child(2n)::before {
	content: "/ ";
	position: absolute;
	left: -30px;
	top: 50%;
	transform: translateY(-50%);
}


/********* Обнуление *********/
* {
	margin: 0;
	padding: 0;
	border: 0;
}

*,
*:before,
*:after {
	box-sizing: border-box;
}

:focus,
:active {
	outline: none;
}

a:focus,
a:active {
	outline: none;
}

nav,
footer,
header,
aside {
	display: block;
}

html,
body {
	width: 100%;

	-ms-text-size-adjust: 100%;
	-moz-text-size-adjust: 100%;
	-webkit-text-size-adjust: 100%;
}

input,
button,
textarea {
	font-family: inherit;
}

input,
textarea {
	overflow: hidden;
}

input::-ms-clear {
	display: none;
}

button {
	cursor: pointer;
}

button::-moz-focus-inner {
	padding: 0;
	border: 0;
}

a,
a:visited,
a:hover {
	text-decoration: none;
}

img {
	vertical-align: top;
}

a,
label {
	-webkit-tap-highlight-color: transparent;
}

h1,
h2,
h3,
h4,
h5,
h6 {
	font-size: inherit;
	font-weight: inherit;
}

table,
caption,
tbody,
tfoot,
thead,
tr,
th,
td {
	margin: 0;
	padding: 0;
	border: none;
	font-size: 100%;
	font: inherit;
	vertical-align: baseline;
	border-collapse: separate;
}

table {
	border-collapse: separate;
	border-spacing: 0;
}"""
