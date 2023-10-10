# SPDX-License-Identifier: LGPL-2.1+

from collections.abc import Iterable

from mkosi.distributions import centos
from mkosi.installer.dnf import Repo
from mkosi.state import MkosiState


class Installer(centos.Installer):
    @classmethod
    def pretty_name(cls) -> str:
        return "RHEL UBI"

    @staticmethod
    def gpgurls(state: MkosiState) -> tuple[str, ...]:
        return ("https://access.redhat.com/security/data/fd431d51.txt",)

    @classmethod
    def repository_variants(cls, state: MkosiState, repo: str) -> Iterable[Repo]:
        if state.config.local_mirror:
            yield Repo(repo, f"baseurl={state.config.local_mirror}", cls.gpgurls(state))
        else:
            assert state.config.mirror

            v = state.config.release
            yield Repo(
                f"ubi-{v}-{repo}-rpms",
                f"baseurl={centos.join_mirror(state.config.mirror, f'ubi{v}/{v}/$basearch/{repo}/os')}",
                cls.gpgurls(state),
            )
            yield Repo(
                f"ubi-{v}-{repo}-debug-rpms",
                f"baseurl={centos.join_mirror(state.config.mirror, f'ubi{v}/{v}/$basearch/{repo}/debug')}",
                cls.gpgurls(state),
                enabled=False,
            )
            yield Repo(
                f"ubi-{v}-{repo}-source",
                f"baseurl={centos.join_mirror(state.config.mirror, f'ubi{v}/{v}/$basearch/{repo}/source')}",
                cls.gpgurls(state),
                enabled=False,
            )
            if repo == "codeready-builder":
                yield Repo(
                    f"ubi-{v}-{repo}",
                    f"baseurl={centos.join_mirror(state.config.mirror, f'ubi{v}/{v}/$basearch/{repo}/os')}",
                    cls.gpgurls(state),
                    enabled=False,
                )

    @classmethod
    def repositories(cls, state: MkosiState, release: int) -> Iterable[Repo]:
        yield from cls.repository_variants(state, "baseos")
        yield from cls.repository_variants(state, "appstream")
        yield from cls.repository_variants(state, "codeready-builder")
