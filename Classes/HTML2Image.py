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
        width = 550
        height = 340

        if not saved:
            if calc.split_values is not None and len(calc.split_values) > 2:
                height += 35 * len(calc.split_values)
            elif len(calc.tp_ratio) > 1:
                height += 20 * len(calc.tp_ratio)

        html_value = get_html_from_calc(user_id, calc, saved)

        file_name = f'{user_id}.png'
        a = self.hti.screenshot(
            save_as=file_name,
            html_str=f"""
				<link rel="stylesheet" href="style.css" />
				<div class="container">
					<div class="main">{html_value}</div>
				</div>
    		""",
            css_str=css_template + f"""
				.main {{
					width: {width}px;
					height: {height}px;
				}}
			""",
        )

        return f'{self.path}/{file_name}'


css_template = """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700;800&display=swap');

body,
.container {
	font-family: 'Montserrat';
	font-weight: 500;
	line-height: 1.5;

	font-size: 19px;
}

.main {
	border-radius: 20px;
	padding: 20px;
	margin: 0 auto;
	width: 500px;
	height: 700px;
	background: #fcfcfc;
	color: #111111;
}

.title {
	font-weight: 800;
}

.block {
	padding: 8px 0;
}

.inline_block {
	display: flex;
	align-items: center;
	gap: 0 10px;
}

.point {
	position: relative;
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 0 5px;
}

.point .name {
	position: relative;
	padding-left: 12px;
}

.point:first-child .name::before {
	content: "";
	position: absolute;
	left: 0px;
	top: 50%;
	transform: translateY(-50%);

	width: 4px;
	height: 4px;
	border-radius: 50%;
	background: #111111;
}

.point p {
	white-space: nowrap;
}

.name::after {
	content: ':';
}

.value {
	font-weight: 700;
}

.value.flex {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
}

.tp {
	gap: 0 10px;
}

.profit {
	gap: 0;
}

.profit .value {
	padding: 0 7px;
}

.profit .value {
	position: relative;
}

.profit .value::before {
	content: "";
	position: absolute;
	height: 16px;
	width: 1px;
	background: #111;
	right: 1px;
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
