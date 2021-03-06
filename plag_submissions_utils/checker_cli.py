#!/usr/bin/env python
# coding: utf-8

import argparse
import sys

import logging

from plag_submissions_utils import common_runner
from plag_submissions_utils.common.submissions import run_over_submissions
from plag_submissions_utils.common.stats import StatCollector
from plag_submissions_utils.common.stats import SrcStatCollector
from plag_submissions_utils.common.stats import print_mod_types_stat
from plag_submissions_utils.common.ir_utils import calc_various_similarity

def run_v1(opts):
    common_run(opts, "1")

def fix_v1(opts):
    common_runner.fix(
        opts.archive, opts.output_file, "1",
        spell_checker_whitelist = opts.spell_checker_whitelist)

def run_v2(opts):
    common_run(opts, "2")

def fix_v2(opts):
    common_runner.fix(
        opts.archive, opts.output_file, "2",
        spell_checker_whitelist = opts.spell_checker_whitelist)

def run_v3(opts):
    common_run(opts, "3")

def fix_v3(opts):
    common_runner.fix(
        opts.archive, opts.output_file, "3",
        spell_checker_whitelist = opts.spell_checker_whitelist)

def common_run(opts, version):
    metrics, errors, stat = common_runner.run(opts.archive, version)

    print("Статистика")
    for m in metrics:
        print("%s %s"  % ("!" * m.get_violation_level(), m))

    print()
    print("Ошибки")
    print("\n".join(str(e) for e in errors))


def collect_stat(opts):
    stat_collector = StatCollector()
    def proc_arc(susp_id, _, meta_file_path):
        chunks, _ = common_runner.create_chunks(
            susp_id, meta_file_path)
        stat_collector(chunks)

    run_over_submissions(opts.archive_dir, proc_arc)
    print_mod_types_stat(stat_collector, sys.stdout)

def collect_src_stat(opts):
    stat_collector = SrcStatCollector()
    def proc_arc(susp_id, _, meta_file_path):
        chunks, _ = common_runner.create_chunks(
            susp_id, meta_file_path)
        stat_collector(chunks)

    run_over_submissions(opts.archive_dir, proc_arc)
    stat_collector.print_stat(sys.stdout)


def common_fix_args(parser):
    parser.add_argument("--archive", "-a", required=True)
    parser.add_argument("--output_file", "-o", required=True)
    parser.add_argument("--spell_checker_whitelist", "-w", nargs='*', default=[])

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true")

    subparsers = parser.add_subparsers(help='different versions')

    v1_parser = subparsers.add_parser('v1')

    v1_parser.add_argument("--archive", "-a", required=True)
    v1_parser.set_defaults(func = run_v1)

    fix_v1_parser = subparsers.add_parser('fix_v1')
    common_fix_args(fix_v1_parser)
    fix_v1_parser.set_defaults(func = fix_v1)

    v2_parser = subparsers.add_parser('v2')

    v2_parser.add_argument("--archive", "-a", required=True)
    v2_parser.set_defaults(func = run_v2)

    fix_v2_parser = subparsers.add_parser('fix_v2')
    common_fix_args(fix_v2_parser)
    fix_v2_parser.set_defaults(func = fix_v2)

    v3_parser = subparsers.add_parser('v3')

    v3_parser.add_argument("--archive", "-a", required=True)
    v3_parser.set_defaults(func = run_v3)

    fix_v3_parser = subparsers.add_parser('fix_v3')
    common_fix_args(fix_v3_parser)
    fix_v3_parser.set_defaults(func = fix_v3)

    stat_parser = subparsers.add_parser('stat')
    stat_parser.add_argument("--archive_dir", "-d", required=True)
    stat_parser.set_defaults(func = collect_stat)

    src_stat_parser = subparsers.add_parser('src_stat')
    src_stat_parser.add_argument("--archive_dir", "-d", required=True)
    src_stat_parser.set_defaults(func = collect_src_stat)

    chunks_sim_parser = subparsers.add_parser('chunks_sim')
    chunks_sim_parser.add_argument("--archive_dir", "-d", required=True)
    chunks_sim_parser.add_argument("--normalize", "-n", default=False, action='store_true')
    chunks_sim_parser.add_argument("--skip_stop_words", "-s", default=False,
                                   action='store_true')
    chunks_sim_parser.set_defaults(func = calc_various_similarity)

    args = parser.parse_args()

    FORMAT="%(asctime)s %(levelname)s: %(name)s: %(message)s"
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format = FORMAT)

    try:
        args.func(args)

    except Exception as e:
        logging.exception("Error: %s", e)

if __name__ == '__main__' :
    main()
