{ArgumentParser} = require 'argparse'
map = require 'through2'
path = require 'path'
split = require 'split2'

packageInfo = require '../package'

argparser = new ArgumentParser(
  addHelp: true
  description: packageInfo.description + ' The fdupes-style file group list is
  read from STDIN, files in matching dirs that can be safely deleted are written
  to STDOUT, and file groups that aren\'t matched or cannot be safely deleted
  are written to STDERR.'
  version: packageInfo.version
)

argparser.addArgument(['dirs'],
  metavar: 'DIRECTORY'
  nargs: '+'
  help: "The directories to select."
)

isParentDir = (from, to) ->
  diff = path.relative(from, to)
  if diff is '' then return true
  for segment in diff.split(path.sep)
    if segment isnt '..' then return false
  return true

makeGroups = ->
  currentFileGroup = []
  map(objectMode: true,
    (line, enc, cb) ->
      line = line.toString()
      #console.log JSON.stringify line
      if line is '' and currentFileGroup.length isnt 0
        @push(currentFileGroup)
        currentFileGroup = []
      else if line isnt ''
        currentFileGroup.push(line)
      cb()
    (cb) ->
      if currentFileGroup.length isnt 0 then @push(currentFileGroup)
      cb()
  )

selectDirs = (stream, dirs) ->
  stream.pipe(
    split()
  ).pipe(
    makeGroups()
  ).pipe(map(objectMode: true, (group, enc, cb) ->
    if group.length < 2
      throw new Error("Found group with less than 2 files:
      #{JSON.stringify(group)}")

    matchedFiles = []
    nonMatchedFiles = []
    for file in group
      if file.trim() is '' then throw new Error(JSON.stringify(file))
      fileDir = path.parse(file).dir
      for dir in dirs
        if isParentDir(fileDir, dir)
          matchedFiles.push(file)
          break

      if file not in matchedFiles then nonMatchedFiles.push(file)

    if nonMatchedFiles.length is 0
      # nothing in the group can be deleted because we would delete all copies
      # of the file
      console.error(group.join('\n') + '\n')
    else
      if nonMatchedFiles.length isnt 1
        # if it were only 1 file, then it could no longer be considered a group
        console.error(nonMatchedFiles.join('\n') + '\n')
      if matchedFiles.length > 0
        console.log(matchedFiles.join('\n'))

    cb()
  ))

process.stdin.setEncoding 'utf8'
argv = argparser.parseArgs()
selectDirs(process.stdin, argv.dirs)
