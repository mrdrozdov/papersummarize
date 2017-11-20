from pyramid.config import Configurator
from ddtrace.contrib.pyramid import trace_pyramid


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['datadog_trace_service'] = 'papersummarize-web'
    config = Configurator(settings=settings)
    trace_pyramid(config)
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.include('.security')
    config.scan()
    return config.make_wsgi_app()

