const { ArgumentParser } = require('argparse')
const { selectDirs } = require('./select-dirs')
const packageInfo = require('../package')

const argparser = new ArgumentParser({
  addHelp: true,
  description: `${packageInfo.description} The fdupes-style file group list is read from STDIN, files in matching dirs that can be safely deleted are written to STDOUT, and file groups that aren't matched or cannot be safely deleted are written to STDERR.`,
  version: packageInfo.version
})

argparser.addArgument(['dirs'], {
  metavar: 'DIRECTORY',
  nargs: '+',
  help: 'The directories to select.'
})

process.stdin.setEncoding('utf8')
const argv = argparser.parseArgs()
selectDirs(process.stdin, argv.dirs)
