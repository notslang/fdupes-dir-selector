const map = require('through2')
const path = require('path')
const split = require('split2')

const isParentDir = (from, to) => {
  const diff = path.relative(from, to)
  if (diff === '') {
    return true
  }
  for (const segment of diff.split(path.sep)) {
    if (segment !== '..') {
      return false
    }
  }
  return true
}

// check if a given file exists within any of the directories in the list
const fileBelongsToADirectory = (file, dirs) => {
  const fileDir = path.parse(file).dir
  for (const dir of dirs) {
    if (isParentDir(fileDir, dir)) {
      return true
    }
  }
  return false
}

const makeGroups = () => {
  let currentFileGroup = []
  return map({ objectMode: true }, (line, enc, cb) => {
    line = line.toString()
    if (line === '' && currentFileGroup.length !== 0) {
      // blank lines separate file groups. the current file group is finished
      // so start a new one
      this.push(currentFileGroup)
      currentFileGroup = []
    } else if (line.trim() !== '') {
      // the line is a file, add it to the group
      currentFileGroup.push(line)
    } else {
      throw new Error(`Found a bad line: ${JSON.stringify(line)}`)
    }
    return cb()
  }, (cb) => {
    // flush out last file group before ending
    if (currentFileGroup.length !== 0) {
      this.push(currentFileGroup)
    }
    return cb()
  })
}

const handleDirGroup = (dirs, group, enc, cb) => {
  if (group.length < 2) {
    // sanity check, fdupes files should not have groups of size 1
    throw new Error(`Found group with less than 2 files: ${JSON.stringify(group)}`)
  }

  const matchedFiles = []
  const nonMatchedFiles = []

  for (const file of group) {
    // sort the files into categories, files that are contained in the provided
    // director(y|ies) and files that are not
    if (fileBelongsToADirectory(file, dirs)) {
      matchedFiles.push(file)
    } else {
      nonMatchedFiles.push(file)
    }
  }

  if (nonMatchedFiles.length === 0) {
    // nothing in the group can be deleted because we would delete all copies
    // of the file
    console.error(group.join('\n') + '\n')
  } else {
    if (nonMatchedFiles.length !== 1) {
      // if it were only 1 file, then it could no longer be considered a group
      console.error(nonMatchedFiles.join('\n') + '\n')
    }

    if (matchedFiles.length > 0) {
      console.log(matchedFiles.join('\n'))
    }
  }
  cb()
}

const selectDirs = (stream, dirs) => {
  return stream.pipe(
    split()
  ).pipe(
    makeGroups()
  ).pipe(
    map({ objectMode: true }, handleDirGroup.bind(this, dirs))
  )
}

module.exports = { selectDirs }
