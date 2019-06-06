# CLUIFuzz

CLUIFuzz is a Command-Line UI Fuzzer. Throws everything from letters to control characters at the given target. For example, it can be used to find ways to crash a restricted CLI program. Simple, hacky, and effective.

### Installation
1) The only external requirement is that the `screen` program is installed on your system. (Preinstalled on MacOS, can be installed on Debian with `apt-get install screen`)
2) Works on both MacOS and Linux.

### Usage
`python cluifuzz.py [-h] binary_location test_name {fuzz,reduce}`

CLUIFuzz has two modes:
1) Fuzz Mode - Identifies an input that crashes the program.
2) Reduce Mode - Reduces the crashing input to only the characters required to crash the program.

Example usage on Nano:
`python cluifuzz.py /Users/maxpl0it/nano/src/nano nano fuzz`

`python cluifuzz.py /Users/maxpl0it/nano-src/src/nano nano reduce`

### Example Uses
The default version of nano that comes with OSX is 2.0.6. When running CLUIFuzz against it, a number of segmentation faults can be found.

##### Identify crashes:

![](/images/fuzz.png)

##### Reduce crashes:

![](/images/reduce.png)
