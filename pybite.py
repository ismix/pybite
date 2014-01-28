import argparse
from base.collector import Collector


def collect(args):
    collector = Collector(args.parser, args.keyword, args.use_proxy)
    try:
        collector.start()
    finally:
        if not (collector.proxy_client is None):
            collector.proxy_client.stop()


def summarize(args):
    print('Summarize!')


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    sp = arg_parser.add_subparsers()
    sp_collect = sp.add_parser('collect', help='Start parsing url for email lists')
    sp_collect.set_defaults(func_name='collect')
    sp_collect.add_argument('-p', '--parser', help='Website parser to use', choices=['yelp'], default='yelp')
    sp_collect.add_argument('-k', '--keyword', help='Keyword to make a search on the site', default=None)
    sp_collect.add_argument('-up', '--use-proxy', help='Use proxy', choices=['tor', 'public'])

    sp_summarize = sp.add_parser('summarize', help='Summarize records collected so far')
    sp_summarize.set_defaults(func_name='summarize')

    args = arg_parser.parse_args()
    eval(args.func_name)(args)
