# fdupes-dir-selector
When I'm using fdupes, I'm often comparing a copy of a large directory tree with an origional directory tree that may or may not have been modified since the copy was made. Tools like [Meld](http://meldmerge.org/) would point out differences in a better way, but don't work on large directory trees (it would crash). I end up using something like `fdupes -r ./dir1 ./dir2` which gives me the following list of file groups:

```
./dir1/FFF5BA07F96B8991EEBC634B688041462DA05C76.torrent
./dir2/FFF6BA07F96B8991EEBC634B688041462DA06C76.torrent

./dir1/FFE763D4B8B73170FA3260A9E4EEDE67662CBA63.torrent
./dir2/FFE763D4B8B73170FA3260A9E4EEDE67662CBA63.torrent

./dir1/FFE6D36ACA3E33A20D4F023C0D17D7B916E67EAB.torrent
./dir2/FFE6D36ACA3E33A20D4F023C0D17D7B916E67EAB.torrent

./dir1/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276.torrent
./dir2/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276.torrent
```

From here, I could do `grep "./dir2/" < fdupes-list | xargs rm` to get rid of all the files in `./dir2` that are duplicated in `./dir1`. However, there might be an oddity in the list like:

```
./dir2/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276.torrent
./dir2/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276 (2).torrent
```

Doing a simple `grep` on a pair like that would cause both files in the group to be removed, destroying all copies of the file. What we really want is to select all the files in `./dir2` (or some combination of directories) where the group contains at least 1 file that wouldn't be selected. That is what `fdupes-dir-selector` is for.

For example, given the following groups:

```
./dir1/004FD30D9BAFE376A24D867FBA71692EED42AD88.torrent
./dir2/004FD30D9BAFE376A24D867FBA71692EED42AD88.torrent
./dir3/004FD30D9BAFE376A24D867FBA71692EED42AD88.torrent

./dir1/089A216CFAC9B38436BF448A07B20DC94793A23D.torrent
./dir3/089A216CFAC9B38436BF448A07B20DC94793A23D.torrent
./dir3/089A216CFAC9B38436BF448A07B20DC94793A23D (2).torrent

./dir2/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276.torrent
./dir2/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276 (2).torrent

./dir1/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276.torrent
./dir2/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276.torrent
```

Running `fdupes-dir-selector ./dir2 ./dir3 < fdupes-list` would give us these files to delete:

```
./dir2/004FD30D9BAFE376A24D867FBA71692EED42AD88.torrent
./dir3/004FD30D9BAFE376A24D867FBA71692EED42AD88.torrent
./dir3/089A216CFAC9B38436BF448A07B20DC94793A23D.torrent
./dir3/089A216CFAC9B38436BF448A07B20DC94793A23D (2).torrent
./dir2/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276.torrent
```

And this leftover group would be emitted to STDERR:

```
./dir2/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276.torrent
./dir2/FFDFEBEB8B6D89FE33EA93A68140F62B6EDC3276 (2).torrent
```
