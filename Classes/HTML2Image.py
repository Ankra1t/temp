from html2image import Html2Image


class HTIService:
    def __init__(self) -> None:
        self.hti = Html2Image(
            output_path='_calc_images',
            size=(200, 320)
        )

    def create_calculation_image(self, file_name: str, value: str):
        width = 400
        height = 600
        print(css_template + f"""
.main {{
	width: {width}px;
	height: {height}px;
}}
""")

        self.hti.screenshot(
            save_as=f'{file_name}.png',
            size=(width, height),
            html_str=f"""
<link rel="stylesheet" href="style.css" />
<div class="container">
	<div class="main">{value}</div>
</div>
""",
            css_str=css_template + f"""
.main {{
	width: {width}px;
	height: {height}px;
}}
""",
        )


hti = HTIService()

css_template = """
body,
.container {
	background: green;
	font-size: 16px;
}

.main {
	padding: 20px;
	margin: 0 auto;
	width: 400px;
	height: 600px;
	background: #ececec;
	color: #2b2b2b;
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