# GPT-Translation-Tools

GPT-Translation-Tools is a command-line Python utility to help with translation tasks.  It makes it easy to run a GPT prompt against each line of a file or each file of a folder, and then combine the answers back together into a document.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
    - [API Key](#api-key)
    - [Subcommands](#subcommands)
    - [Options](#options)
    - [Templating](#templating)

## Installation

To install GPT-Translation-Tools, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/bchurchill/gpt-translation-tools.git
    cd gpt-translation-tools
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Test the installation by running the test script:
    ```sh
    ./test.sh
    ```
   This script will run a series of tests to verify that everything is working correctly. If you see any errors, double-check the installation steps and resolve any issues before proceeding.

## Usage

tool.py is a command-line Python program that serves as an entry point to launch various sub-tools for working with translations and GPT models. The script offers a number of subcommands, each tailored for a specific task.   Each subcommand represents a different tool or functionality. Some options are shared across multiple subcommands, while others are unique to a specific subcommand. When invoking tool.py, you first specify the subcommand and then provide any options relevant to that subcommand.

For example, the general structure of a command could be:

```
./tool.py <subcommand> [options]
```

### API Key

To provide your OpenAI API key to the system, set the environment variable `OPENAI_API_KEY`.  Note that for testing the code without GPT you can use `-m math`.  Instaed of invoking GPT we have a stub that will try and parse any input as a mathematical expression and compute it.

### Subcommands

- `prompt-all`:
    - Description: Runs a prompt against every line of a file.
    - Usage: `./tool.py prompt-all -p <prompt_file> -i <input_file>`

- `prompt-folder`:
    - Description: Runs a prompt against every file in a folder.
    - Usage: `./tool.py prompt-folder -p <prompt_file> -i <input_directory>`

- `map-reduce`:
    - Description: Performs a map-reduce operation on files in a folder by running a mapping prompt against each file and then reducing/summarizing the results with a reducing prompt.  This was intended as an experiment to help with a translate-then-summarize operation.  The results weren't so great.
    - Usage: `./tool.py map-reduce -p <map_prompt_file> -r <reduce_prompt_file> -i <input_directory>`

- `counttokens`:
    - Description: Counts the tokens in the input text.
    - Usage: `./tool.py counttokens -i <input_text>`

- `prompt`:
    - Description: Runs GPT on a single input prompt.
    - Usage: `./tool.py prompt -i <input_text>`

- `download-csv`:
    - Description: Downloads texts into a directory using a CSV file.  This was made for a specific use case, and probably isn't reusable.
    - Usage: `./tool.py download-csv --output-dir <output_directory> -i <input_csv_file>`

- `download-url`:
    - Description: Downloads a single URL.
    - Usage: `./tool.py download-url -u <url> -f <file_name_prefix>`

- `chat`:
    - Description: Initiates a chat with GPT.  This can be helpful when you've run out of your GPT plus and want to keep using GPT-4.
    - Usage: `./tool.py chat`

- `compute-embeddings`:
    - Description: Retrieves embeddings for each line of a file.
    - Usage: `./tool.py compute-embeddings -i <input_file>`

Note: Each subcommand has additional options that can be passed. Refer to the options documentation for details on the options that can be used with each subcommand.

### Options

#### Shared Options (Common to Multiple Subcommands):

These options can be used with most subcommands.

- `-d`, `--debug`: Enable debug output. This flag will make additional details like cost information available in the log file. (Optional)
- `-w`, `--workers`: Number of workers for tasks to be done in parallel. Default is 10. (Optional)
- `--logfile`: File to write log entries to. Defaults to appending '.log' to the output file. The log file contains additional details, for example, cost information and debug information if requested. (Optional)
- `-o`, `--output`: Output file. Defaults to output.txt. This file will contain just the requested output. (Optional)
- `-i`, `--input`: Path to the input text file. (Required for subcommands that require an input file)
- `-L`, `--lines`: Specifies which lines of the file to work on. For example, "2-20" would only read and work on lines 2 through 20. Optional, defaults to processing all lines. This option is useful when only certain lines of the file should be read and worked on. (Optional)

#### GPT Options:

These options are specific to configuring the GPT model.

- `-m`, `--model`: Model to use for translation. Available options are 'gpt-3.5-turbo', 'gpt-4', 'text-ada-001', 'text-babbage-001', 'text-curie-001', 'math'. Default is 'gpt-4'. (Optional)
- `--top-p`: Value of top_p to pass to GPT. Default is 1.0. (Optional)
- `--best-of`: Value of best_of to pass to GPT. Default is 1. (Optional)
- `--max-tokens`: Value of max_tokens to pass to GPT. Default is 9000. (Optional)
- `--gpt-n`: Value of n (number of responses) to pass to GPT. Default is 1. (Optional)

#### Translation Options:

These options are specific to the translation task.

- `--examples-in`: File with example inputs for translation. (Optional)
- `--examples-out`: File with example outputs for translation. (Optional)
- `--examples-embeddings`: File with embeddings of example inputs for translation. (Optional)
- `--wordlist`: JSON file with specific translations to use. (Optional)

#### Input Arguments for Specific Subcommands:

- `--prompt`: Filename with a prompt to provide to GPT. (Used in subcommands: `prompt-all`, `prompt-folder`, `map-reduce`, `chat`)
- `--input-dir`: Input directory path for the 'prompt-folder' and 'map-reduce' subcommands. (Optional)
- `--map-prompt`: Filename with a prompt to provide to GPT for mapping. (Used in the 'map-reduce' subcommand)
- `--reduce-prompt`: Filename with a prompt to provide to GPT for reducing/summarizing. (Used in the 'map-reduce' subcommand)
- `--output-dir`: Output directory for the 'download-csv' subcommand. (Required for 'download-csv' subcommand)
- `-u`, `--url`: URL to download for the 'download-url' subcommand. (Required for 'download-url' subcommand)

### Templating

In `prompt-all`, `prompt-folder`, and `map-reduce` subcommands of
GPT-Translation-Tools, you have the option to use a templating feature that
allows for dynamic expressions within the prompt. This feature enables prompts
to be customized based on the content of the input text, file identifiers, and
pre-defined word lists.  To use this feature, you use curly braces inside of
the prompt to tell the tool that you want to insert data or perform computation
in the prompt.

#### Available Variables for Templating

Enclose any of the following in braces `{}` in the prompt to substitute the value:

 - **LEN**: Represents the word count of the input text.
 - **NEAREST_EXAMPLE_IN**: Holds the input of the nearest example based on GPT embeddings. The Euclidean distance between the embeddings of the input text and the predefined example inputs determines the nearest example input.
 - **NEAREST_EXAMPLE_OUT**: Contains the output corresponding to the nearest example input.
 - **WORDLIST**: If the `--wordlist` parameter is supplied, this variable contains a list of preferred translations of words that appear in the input.
 - **AUTHOR**: Extracts the author from the file name. If the file ID starts with "BH", it represents Baha'u'llah. If it starts with "AB", it represents Abdu'l-Baha.

#### Expressions
Additionally, you can use expressions within the curly braces. This is useful
for performing operations like calculating the length of text or conditionally
displaying content.

For security, only a limited set of expressions are allowed. Specifically, you
can use `min` and `max` functions, the variables provided, and standard
arithmetic operators.

#### Use Cases

Below are two examples that demonstrate how you can utilize the templating feature in prompts:

1. Summarizing a text:

Prompt: 

```
Summarize the text to {min(LEN/3,50)} words
```
            
This template uses the LEN variable to dynamically adjust the number of words for summarization based on the input text's length.

2. Custom translations using preferred word translations and author information:

Prompt: 
```
Translate this text by {AUTHOR} using the following word translations: 

{WORDLIST}
```

This template uses the AUTHOR and WORDLIST variables to dynamically adjust the prompt based on the author information extracted from the file ID and preferred translations in the word list.

By including expressions in curly braces { } within the prompt, the template engine evaluates the expressions and substitutes them with the respective values at runtime.
