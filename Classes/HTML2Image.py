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

        return f'{self.path}/{file_name}', caption


css_template = """
body,
.container {
	font-family: 'Montserrat';

	background: white;
	font-size: 50px;
	line-height: 1.4;
	font-weight: 500;
}

.main {
	padding: 80px;
	margin: 0 auto;
	width: 1280px;
	background: #fbfbfb;
	color: #131313;

	display: flex;
	flex-direction: column;
	gap: 60px;
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

.major {
	display: flex;
	gap: 20px;
	justify-content: space-between;

	padding: 40px;
	border-radius: 20px;
	background: white;
	box-shadow: 0 4px 50px 0 rgba(113, 133, 202, 0.2);
}

.name {
	flex: 0 0 460px;
}

.value {
	flex: 1 1 auto;
	font-weight: 600;
	color: #0094fe;
}

.major {
	background: #0094fe;
	color: white;
}

.major .value {
	color: white;
}

.content {
	border-radius: 20px;
	border: 1px solid rgba(0, 148, 254, 0.3);
	padding: 0 40px;
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
}
"""
