from flask import Flask, render_template
import flask
import jinja2
import timeit
import platform
import cProfile
import cStringIO
import pstats

app = Flask(__name__)
app.jinja_options = app.jinja_options.copy()
app.jinja_options['bytecode_cache'] = jinja2.FileSystemBytecodeCache()


def time_render(template_name, res, times):
    return timeit.timeit(lambda: render_template(template_name, **res),
                         number=times)


def make_django_tutorial_context():
    return {
        "error_message": "error!",
        "poll": {"question": "test_question",
                 "choice_set": {"all": [
                     {"id":x, "choice_text":"choice %s" % x}
                     for x in xrange(4)]
                 }}
    }


def make_results_context():
    return {"results": {"test": {"time_taken": 1, "per_call": 1},
                        "test2": {"time_taken": 1, "per_call": 1},
                        "test3": {"time_taken": 1, "per_call": 1}},
            "platform": {"django_version": 1,
                         "python_version": 2}}


@app.route('/')
def index():
    times = 100

    returner = {}

    for template_name in ["empty_template.html", "stackoverflow_homepage.html",
                          ("django_tutorial_page.html", make_django_tutorial_context),
                          ("results.html", make_results_context)]:
        dict = {}
        if isinstance(template_name, tuple):
            template_name, callable = template_name
            dict = callable()
        time_taken = round(time_render(template_name, dict, times), 5)

        profile = cProfile.Profile()
        prof = profile.runctx("render_template(template_name, **dict)", globals(), locals())
        output = cStringIO.StringIO()
        pstats.Stats(prof, stream=output).strip_dirs().sort_stats(0).print_stats()

        returner[template_name] = {"time_taken": time_taken, "per_call": time_taken / times,
                                   "profile": output.getvalue()}

    return render_template("results.html", results=returner, platform={
        "django_version": flask.__version__,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "debug": app.debug
    })


if __name__ == '__main__':
    app.run(debug=False)
