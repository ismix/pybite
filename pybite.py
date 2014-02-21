import argparse
from base.collector import Collector
from base.summarizer import Summarizer
import logging
import time


def collect(args):
    if args.verbose:
        logging.basicConfig(filename='dbg_'+args.parser+'_'+str(time.time())+'.log', filemode='w', level=logging.DEBUG)

    parser_params = process_param_string(args.parser_params)
    collector = Collector(args.parser, args.use_proxy, parser_params)
    try:
        collector.start()
    finally:
        if collector.proxy_client is not None:
            collector.proxy_client.stop()


def summarize(args):
    filters = process_param_string(args.filter)
    Summarizer().run(filters)


def process_param_string(param_str):
    if param_str is None:
        return None

    params = {}
    try:
        pairs = param_str.split(',')
        for pair in pairs:
            [k, v] = pair.split('=')
            params[k] = v
        return params
    except:
        print "Invalid filter string, correct pattern is field1=value1,field2=value2"
        raise SystemExit

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    sp = arg_parser.add_subparsers()
    sp_collect = sp.add_parser('collect', help='Start parsing url for email lists')
    sp_collect.set_defaults(func_name='collect')
    sp_collect.add_argument('-p', '--parser', help='Website parser to use', choices=['yelp'], default='yelp')
    sp_collect.add_argument('-pp', '--parser-params',
                            help='Parser specific parameters. This string is field=value pairs separated with commas.',
                            default=None)
    sp_collect.add_argument('-up', '--use-proxy', help='Use proxy', choices=['tor', 'public'])
    sp_collect.add_argument('-v', '--verbose', help='Verbose output', action='store_true')

    sp_summarize = sp.add_parser('summarize', help='Summarize records collected so far')
    sp_summarize.set_defaults(func_name='summarize')
    sp_summarize.add_argument('-f', '--filter',
                              help='Show filtered count as well. '
                                   'Filter string is field=value pairs separated with commas.',
                              default=None)

    args = arg_parser.parse_args()
    eval(args.func_name)(args)
