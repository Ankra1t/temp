from html2image import Html2Image

from common.calculation import get_html_from_calc
from models import Calculation


class HTIService:
    def __init__(self) -> None:
        self.path = '_calc_images'
        self.hti = Html2Image(
            output_path=self.path,
            custom_flags=[
                '--headless',
                '--no-sandbox',
                '--enable-features=ConversionMeasurement,AttributionReportingCrossAppWeb',
                '--enable-chrome-browser-cloud-management',
                '--ignore-certificate-errors"',
                '--disable-gpu'
            ]
        )

    def create_calculation_image(self, user_id: int, calc: Calculation, saved=False):
        width = 500
        height = 340

        if not saved:
            if calc.split_values is not None and len(calc.split_values) > 2:
                height += 30 * len(calc.split_values)
            elif len(calc.tp_ratio) > 1:
                height += 20 * len(calc.tp_ratio)

        html_value = get_html_from_calc(user_id, calc, saved)

        file_name = f'{user_id}.png'
        a = self.hti.screenshot(
            save_as=file_name,
            size=(width, height),
            html_str=f"""
            	<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700;800&display=swap" rel="stylesheet">
				<link rel="stylesheet" href="style.css" />
				<div class="container">
					<div class="main">{html_value}</div>
				</div>
    		""",
            css_str=css_template + f"""
				.main {{
					width: {width}px;
				}}
			""",
        )

        return f'{self.path}/{file_name}'


css_template = """
body,
.container {
	font-family: 'Montserrat';
	font-weight: 500;
	line-height: 1.2;
	font-size: 18px;
}

.main {
	border-radius: 20px;
	padding: 15px;
	margin: 0 auto;
	width: 480px;
	background: #fff;
	color: #111111;

	display: flex;
	flex-direction: column;
	gap: 8px;
}

.header {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.title {
	font-weight: 800;
}

.header_name {
	display: flex;
	align-items: center;
	gap: 12px;
}

.buy,
.sell {
	border-radius: 10px;
	padding: 8px 12px;
	background: #f7f7f7;
	font-size: 0.8em;
	font-weight: 600;
}

.buy {
	color: #06bd32;
}
.sell {
	color: #f36a77;
}

.row {
	display: flex;
	gap: 10px;
}

.block {
	width: 100%;
	padding: 10px;
	background: #f7f7f7;
	border-radius: 20px;
}

.value {
	font-weight: 600;
	white-space: nowrap;
	text-align: center;
}

.name {
	font-size: 0.9em;
	text-align: center;
}

.tp {
	font-size: 0.9em;
	line-height: 1.4;
	display: flex;
	flex-wrap: wrap;
	gap: 0 14px;
}

.profit {
	display: flex;
	flex-wrap: wrap;
}

.tp, .profit {
	margin-top: 7px;
}

.tp_default {
	display: flex;
	align-items: center;
	gap: 7px;
	white-space: nowrap;
}

.tp_item {
	width: 100%;
	display: flex;
	justify-content: space-between;

	white-space: nowrap;
}

.tp_val {
	flex: 0 1 100px;
	display: flex;
	justify-content: space-between;
}

.tp_count {
	flex: 0 1 70%;
	display: flex;
	justify-content: space-between;
}

.profit .value {
	position: relative;
	padding: 0 7px;
}

.profit .value:not(:last-child)::after {
	content: "";
	position: absolute;
	top: 50%;
	right: 0;
	transform: translateY(-50%);
	width: 1px;
	height: 50%;
	background: black;
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