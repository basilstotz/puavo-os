prefix = /usr
exec_prefix = $(prefix)
bindir = $(exec_prefix)/bin
sbindir = $(exec_prefix)/sbin
sysconfdir = /etc
datarootdir = $(prefix)/share

INSTALL = install
INSTALL_PROGRAM = $(INSTALL)
INSTALL_DATA = $(INSTALL) -m 644

.PHONY: all
all:
	${MAKE} -C packages all

.PHONY: installdirs
installdirs:
	mkdir -p $(DESTDIR)$(bindir)
	mkdir -p $(DESTDIR)$(sbindir)
	mkdir -p $(DESTDIR)$(sysconfdir)/puavo-pkg
	mkdir -p $(DESTDIR)$(datarootdir)/puavo-conf/definitions
	${MAKE} -C packages installdirs

# XXX We do not install puavo-pkg-updater, puavo-pkg-updater.conf and
# XXX puavo-update-remote-pkginstaller-bundle because we probably
# XXX do not need them anymore.

.PHONY: install
install: installdirs
	$(INSTALL_DATA) -t $(DESTDIR)$(datarootdir)/puavo-conf/definitions \
                puavo-pkgs-ui.json
	$(INSTALL_PROGRAM) -t $(DESTDIR)$(bindir) \
		puavo-pkg-wine-helper

	$(INSTALL_PROGRAM) -t $(DESTDIR)$(sbindir) \
		puavo-pkg \
		puavo-pkgs-ui \
		puavo-pkg-update \
		puavo-pkg-update-from-gui \
		puavo-pkg-update-repository \
		puavo-test-puavo-pkg-installers

	$(INSTALL_DATA) -t $(DESTDIR)$(sysconfdir)/puavo-pkg \
		puavo-pkg.conf

	${MAKE} -C packages install

.PHONY: clean
clean:
	${MAKE} -C packages clean
