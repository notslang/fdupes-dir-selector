# fdupes-dir-selector

`fdupes-dir-selector` is a tool for safely selecting groups of duplicate files identified by [`fdupes`](https://github.com/adrianlopezroche/fdupes) or [`jdupes`](https://github.com/jbruchon/jdupes).

For example, after running `fdupes` on a large filesystem, you want to delete duplicates that exist a particular set of directories. This tool will process the list of duplicate files that `fdupes` produced and select all the files within those directories that can be deleted while still leaving at least one copy of the file on the system.

## why?

When I'm using fdupes, I'm often comparing a large directory tree with a backup of that directory tree that may or may not have been modified since the backup was made. Tools like [Meld](http://meldmerge.org/) or [fslint](https://www.pixelbeat.org/fslint/) would allow me to delete duplicates, but don't work on large directory trees (it would crash). I end up using something like `fdupes -r ./dir1 ./dir2` which gives me a list of file groups like:

```
./dir1/image.jpg
./dir2/image.jpg

./dir1/index.html
./dir2/home.html

./dir1/styles.css
./dir2/styles.css
```

From here, I could do `grep "./dir2/" < fdupes-list | tr '\n' '\0' | xargs -0 rm` to get rid of all the files in `./dir2` that are duplicated in `./dir1`. However, there might be an oddity in the list like:

```
./dir2/icon.png
./dir2/icon (2).png
```

Doing a simple `grep` on a pair like that would cause both files in the group to be removed, destroying all copies of the file. What we really want is to select all the files in `./dir2` (or some combination of directories) where the group contains at least 1 file that wouldn't be selected. That is what `fdupes-dir-selector` is for.

For example, given the following groups:

```
./dir1/image.jpg
./dir2/image.jpg
./dir3/image.jpg

./dir1/index.html
./dir2/home.html
./dir2/index (2).html
./dir3/index.html

./dir1/script.js
./dir2/script.js

./dir2/icon.png
./dir2/icon (2).png
```

Running `fdupes-dir-selector ./dir2 ./dir3 < fdupes-list` would give us these files to delete:

```
./dir2/image.jpg
./dir3/image.jpg
./dir2/home.html
./dir2/index (2).html
./dir3/index.html
./dir2/script.js
```

And this leftover group would be emitted to STDERR:

```
./dir2/icon.png
./dir2/icon (2).png
```
