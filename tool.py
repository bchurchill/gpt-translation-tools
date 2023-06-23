#!/usr/bin/python3

import argparse
import sys
import datetime
import asyncio

from src.chat import chat
from src.counttokens import count_tokens
from src.csv_downloader import csv_download
from src.embeddings import compute_embeddings
from src.prompt import prompt_one
from src.prompt_all import prompt_all
from src.prompt_folder import prompt_folder
from src.logger import Logger
from src.mapreduce import map_reduce
from src.url_downloader import url_download


def quote_argument(arg):
    if ' ' in arg or '"' in arg or "'" in arg:
        return '"' + arg.replace("\"", "\\\"") + '"'
    return arg

# Reconstruct the command string with quotes added when necessary
def get_invocation():
    return ' '.join(quote_argument(arg) for arg in sys.argv)

def main():

    common_args = argparse.ArgumentParser(add_help=False)
    common_args.add_argument('-d', '--debug', action="store_true", help="enable debug output")
    common_args.add_argument('-w', '--workers', type=int, default=10,
                              help='Number of workers for tasks to be done in parallel.')
    common_args.add_argument('--logfile', type=str, default=None,
                             help="File to write log entries to.  Defaults to putput file with '.log' appended.")
    common_args.add_argument('-o', '--output', type=str, default="output.txt",
                                    help='Output file.  Defaults to output.txt.')

    gpt_args = argparse.ArgumentParser(add_help=False)
    gpt_args.add_argument('-m', '--model', type=str, default='gpt-4',
                              choices=['gpt-3.5-turbo', 'gpt-4', 'text-ada-001', 'text-babbage-001', 'text-curie-001', 'math'],
                              help='Model to use for translation. Defaults to gpt-4')
    gpt_args.add_argument('--top-p', type=float, default=1.0, help="value of top_p to pass to GPT")
    gpt_args.add_argument('--best-of', default=1, type=int, help="value of best_of to pass to GPT")
    gpt_args.add_argument('--max-tokens', default=9000, type=int, help="value of max_tokens to pass to GPT")
    gpt_args.add_argument('--gpt-n', default=1, type=int, help="value of n (number responses) to pass to GPT")

    input_args = argparse.ArgumentParser(add_help=False)
    input_args.add_argument('-i', '--input', type=str, required=True,
                              help='Input text to count tokens')
    input_args.add_argument('-L', '--lines', type=str, default=None,
                              help='Which lines to work on, e.g. 2-20.  Optional, defaults to all.')


    translation_args = argparse.ArgumentParser(add_help=False)
    translation_args.add_argument('--examples-in', type=str, default=None, help='File with example inputs')
    translation_args.add_argument('--examples-out', type=str, default=None, help='File with example outputs')
    translation_args.add_argument('--examples-embeddings', type=str, default=None, help='File with embeddings of example inputs')
    translation_args.add_argument('--wordlist', type=str, default=None, help='JSON file with specific translations to use.')


    # Define argparse parser
    parser = argparse.ArgumentParser(description='Translation tool')
    # Define subcommands
    subparsers = parser.add_subparsers(title='Subcommands')

    # Subcommand: promptall
    parser_promptall = subparsers.add_parser('prompt-all', help='Run a prompt against every line of a file', parents=[common_args, gpt_args, input_args, translation_args])
    parser_promptall.add_argument('-p', '--prompt', type=str, required=True,
                                    help='Filename with a prompt to provide to GPT.')
    parser_promptall.set_defaults(func=prompt_all)

    # Subcommand: prompt-folder
    parser_prompt_folder = subparsers.add_parser('prompt-folder', help='Run a prompt against every file in a folder', parents=[common_args, gpt_args, translation_args])
    parser_prompt_folder.add_argument('-p', '--prompt', type=str, required=True,
                                    help='Filename with a prompt to provide to GPT.')
    parser_prompt_folder.add_argument('-i', '--input-dir', type=str, required=True,
                                    help='Input text to count tokens')
    parser_prompt_folder.set_defaults(func=prompt_folder)

    # Subcommand: mapreduce
    parser_prompt_folder = subparsers.add_parser('map-reduce', help='Run a prompt against every file in a folder', parents=[common_args, gpt_args, translation_args])
    parser_prompt_folder.add_argument('-p', '--map-prompt', type=str, required=True,
                                    help='Filename with a prompt to provide to GPT for mapping.')
    parser_prompt_folder.add_argument('-r', '--reduce-prompt', type=str, required=True,
                                    help='Filename with a prompt to provide to GPT for reducing/summarizing.')
    parser_prompt_folder.add_argument('-i', '--input-dir', type=str, required=True,
                                    help='Input text to count tokens')
    parser_prompt_folder.set_defaults(func=map_reduce)

    # Subcommand: counttokens
    parser_counttokens = subparsers.add_parser('counttokens', help='Count tokens in text', parents=[common_args, gpt_args, input_args])
    parser_counttokens.set_defaults(func=count_tokens)

    # Subcommand: prompt
    parser_prompt = subparsers.add_parser('prompt', help='Run GPT on one input', parents=[common_args, gpt_args, input_args])
    parser_prompt.set_defaults(func=prompt_one)

    # Subcommand: download-csv
    parser_download_csv = subparsers.add_parser('download-csv', help='Download texts into directory using a CSV file', parents=[common_args, input_args])
    parser_download_csv.add_argument('--output-dir', type=str, required=True, help='Output directory.')
    parser_download_csv.set_defaults(func=csv_download)

    # Subcommand: download-url
    parser_download_url = subparsers.add_parser('download-url', help='Download a single URL', parents=[common_args])
    parser_download_url.add_argument('-u', '--url', type=str, required=True, help='URL to download.')
    parser_download_url.add_argument('-f', '--file', type=str, required=True, help='File name prefix')
    parser_download_url.add_argument('--length-hint', type=int, default=0, help='How many words we expect to find')
    parser_download_url.set_defaults(func=url_download)

    # Subcommand: chat
    parser_chat = subparsers.add_parser('chat', help='Chat with GPT', parents=[common_args, gpt_args])
    parser_chat.add_argument('-p', '--prompt', type=str, help="System prompt for chat.", default="You are a helpful assistant.")
    parser_chat.set_defaults(func=chat)

    # Subcommand: compute-embeddings
    embeddings = subparsers.add_parser('compute-embeddings', help='Get an embedding for each line of a file', parents=[common_args, gpt_args, input_args])
    embeddings.set_defaults(func=compute_embeddings)

    # Parse arguments
    args = parser.parse_args()
    asyncio.run(start(args, parser))


async def start(args, parser):
    # Call subcommand function
    if hasattr(args, 'func') and callable(args.func):
        try:
            logger = Logger(args)
            logger.log(get_invocation())
            logger.debug(sys.argv)
            logger.debug(f"args={args}")

            starttime = datetime.datetime.now()
            logger.log("")
            logger.log(f"Starting at {starttime.strftime('%B %d %Y %I:%M %p')}")
            logger.log("")

            await args.func(args, logger)
        except Exception as e:
            logger.fatal_error(e)
    else:
        parser.print_help()
        sys.exit(1)

    endtime = datetime.datetime.now()
    logger.log(f"Finished at {endtime.strftime('%B %d %Y %I:%M %p')}")
    duration = endtime - starttime
    duration_seconds = int(duration.total_seconds())
    logger.log(f"Total duration: {duration_seconds} seconds")
    logger.log(f"  ({int(duration_seconds/3600)} hours, {int(duration_seconds%3600/60)} minutes, {duration_seconds%60} seconds)")



if __name__ == '__main__':
    main()
