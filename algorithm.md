<!-- markdownlint-disable MD041 -->

## Matching

zoxide uses a simple, predictable algorithm for resolving queries:

1. All matching is case-insensitive.
   - `z foo` matches `/foo` as well as `/FOO`.
2. All terms must be present (including slashes) within the path, in order.
   - `z fo ba` matches `/foo/bar`, but not `/bar/foo`.
   - `z fo / ba` matches `/foo/bar`, but not `/foobar`.
3. The last component of the last keyword must match the last component of the path.
   - `z bar` matches `/foo/bar`, but not `/bar/foo`.
   - `z foo/bar` (last component: `bar`) matches `/foo/bar`, but not `/foo/bar/baz`.
4. Matches are returned in descending order of [frecency](#Frecency).

## Frecency

Each directory in zoxide is assigned a _score_, starting with 1 the first time it is accessed. Every subsequent access increases the score by 1. When a query is made, we calculate _frecency_ based on the last time the directory was accessed:

| Last access time     | Frecency    |
| -------------------- | ----------- |
| Within the last hour | `score * 4` |
| Within the last day  | `score * 2` |
| Within the last week | `score / 2` |
| Otherwise            | `score / 4` |

## Aging

zoxide uses a parameter called `_ZO_MAXAGE` to limit the number of entries in the database based on usage patterns. If the total score of the directories in the database exceeds this value, we divide each directory's score by a factor _k_ such that the new total score becomes ~90% of `_ZO_MAXAGE`. Thereafter, if the new score of any directory falls below 1, we remove it from the database.

Theoretically, the maximum number of directories in the database is `4 * _ZO_MAXAGE`, although it is lower in practice.

## Pruning

Entries that no longer exist on the filesystem and are older than 90 days are lazily pruned from the database.