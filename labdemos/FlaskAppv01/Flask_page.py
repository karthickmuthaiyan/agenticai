from flask import Flask, render_template_string, request
from utils.gutenberg_tool_calling import answer_question
from utils.gutenberg_tool_calling_structured_output import answer_question as answer_question_structured

app = Flask(__name__)

INDEX_TEMPLATE = """
<!doctype html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>AI Demos</title>
	<style>
		:root { font-family: Inter, ui-sans-serif, system-ui, sans-serif; color: #e8eefc; background: #0b1020; }
		* { box-sizing: border-box; }
		body { margin: 0; min-height: 100vh; background: radial-gradient(circle at top right, #26366d 0, #0b1020 48%); }
		nav { max-width: 1050px; margin: auto; padding: 28px 24px; display: flex; justify-content: space-between; align-items: center; }
		.brand { color: #fff; font-weight: 800; letter-spacing: .04em; text-decoration: none; }
		nav a:not(.brand) { color: #aebce0; text-decoration: none; margin-left: 24px; }
		nav a:hover { color: #fff; }
		main { max-width: 1050px; margin: 8vh auto; padding: 0 24px; }
		.hero, .card { background: rgba(20, 29, 57, .82); border: 1px solid rgba(154, 174, 232, .2); border-radius: 24px; box-shadow: 0 24px 70px rgba(0,0,0,.28); backdrop-filter: blur(12px); }
		.hero { padding: clamp(32px, 7vw, 80px); }
		h1 { margin: 0 0 16px; font-size: clamp(2.4rem, 6vw, 4.5rem); line-height: 1.05; }
		p { color: #b8c3df; line-height: 1.7; }
		.actions { display: flex; flex-direction: column; align-items: flex-start; gap: 14px; margin-top: 32px; }
		.link { color: #aebce0; font-weight: 700; text-decoration: underline; text-underline-offset: 4px; }
		.link:hover { color: #fff; }
		.search { width: 100%; max-width: 520px; margin-top: 28px; padding: 15px 16px; border: 1px solid #44527c; border-radius: 12px; background: #111a35; color: #fff; font-size: 1rem; }
	</style>
</head>
<body>
	<nav><a class="brand" href="{{ url_for('home') }}">✦ AI DEMOS</a><span><a href="{{ url_for('about') }}">About</a></span></nav>
	<main><section class="hero"><h1>Explore intelligent ideas.</h1><p>Simple, practical demonstrations of modern AI capabilities—designed to be curious, useful, and easy to try.</p><input class="search" id="function-search" type="search" placeholder="Search available functions..." aria-label="Search available functions"><div class="actions" id="function-list"><a class="link" href="{{ url_for('answer_question_page') }}">Search Gutenberg →</a><a class="link" href="{{ url_for('answer_question_structured_page') }}">Search Gutenberg (Structured) →</a></div></section></main>
	<script>
		document.getElementById("function-search").addEventListener("input", function () {
			const search = this.value.toLowerCase();
			document.querySelectorAll("#function-list .link").forEach(function (link) {
				link.hidden = !link.textContent.toLowerCase().includes(search);
			});
		});
	</script>
</body>
</html>
"""

QUERY_TEMPLATE = """
<!doctype html>
<html>
<head>
	<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
	<title>AI Demos - {{ page_title }}</title>
	<style>
		:root { font-family: Inter, ui-sans-serif, system-ui, sans-serif; color: #e8eefc; background: #0b1020; } * { box-sizing: border-box; }
		body { margin: 0; min-height: 100vh; background: radial-gradient(circle at top right, #26366d 0, #0b1020 48%); }
		nav { max-width: 1050px; margin: auto; padding: 28px 24px; display: flex; justify-content: space-between; } nav a { color: #aebce0; text-decoration: none; } .brand { color: #fff; font-weight: 800; letter-spacing: .04em; }
		main { max-width: 800px; margin: 8vh auto; padding: 0 24px; } .card { padding: clamp(28px, 6vw, 56px); background: rgba(20,29,57,.85); border: 1px solid rgba(154,174,232,.2); border-radius: 24px; box-shadow: 0 24px 70px rgba(0,0,0,.28); }
		h1 { margin-top: 0; font-size: clamp(2rem, 5vw, 3.5rem); } label { display: block; color: #b8c3df; margin: 28px 0 10px; } input { width: 100%; padding: 15px 16px; border: 1px solid #44527c; border-radius: 12px; background: #111a35; color: #fff; font-size: 1rem; } button { margin-top: 16px; padding: 13px 20px; border: 0; border-radius: 12px; background: linear-gradient(135deg,#7c5cff,#4f8cff); color: #fff; font-weight: 700; cursor: pointer; } h2 { margin-top: 36px; } pre { padding: 18px; overflow: auto; white-space: pre-wrap; color: #cbd8ff; background: #0d1429; border-radius: 12px; } .back { display: inline-block; margin-top: 28px; color: #aebce0; }
	</style>
</head>
<body>
	<nav><a class="brand" href="{{ url_for('home') }}">✦ AI DEMOS</a><a href="{{ url_for('about') }}">About</a></nav>
	<main><section class="card"><h1>{{ page_title }}</h1><p>Submit a query to <code>{{ page_title }}</code>.</p><form method="post">
		<label for="query">Input query:</label>
		<input id="query" name="query" value="{{ query }}" required>
		<button type="submit">Submit</button>
	</form>
	{% if result is not none %}
	<h2>Result</h2>
	<pre>{{ result }}</pre>
	{% endif %}
	<p><a class="back" href="{{ url_for('home') }}">← Back to AI Demos</a></p></section></main>
</body>
</html>
"""


@app.route("/")
def home():
	return render_template_string(INDEX_TEMPLATE)


def render_query_page(page_title, answer_function):
	query_text = request.form.get("query", "")
	result = None
	if request.method == "POST":
		try:
			result = answer_function(query_text)
		except Exception as error:
			result = str(error)
	return render_template_string(QUERY_TEMPLATE, page_title=page_title, query=query_text, result=result)


@app.route("/answer_question", methods=["GET", "POST"])
def answer_question_page():
	return render_query_page("Search Gutenberg", answer_question)


@app.route("/answer_question_structured", methods=["GET", "POST"])
def answer_question_structured_page():
	return render_query_page("Search Gutenberg (Structured)", answer_question_structured)


@app.route("/about")
def about():
	return render_template_string(
		"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>About AI Demos</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:system-ui,sans-serif;color:#e8eefc;background:radial-gradient(circle at top right,#26366d,#0b1020 48%)}.card{max-width:600px;margin:24px;padding:48px;background:#141d39dd;border:1px solid #9aaee833;border-radius:24px;box-shadow:0 24px 70px #0005}h1{font-size:2.6rem;margin-top:0}p{color:#b8c3df;line-height:1.7}a{color:#aebce0}</style></head><body><section class='card'><h1>About AI Demos</h1><p>A collection of focused demonstrations exploring practical, human-friendly AI capabilities.</p><a href='/'>← Back to AI Demos</a></section></body></html>"""
	)


if __name__ == "__main__":
	app.run(debug=True)

