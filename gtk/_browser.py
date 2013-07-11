#!/usr/bin/env python

from ..oauth import get_drive_service
from ..drive import GoogleDrive
from _widgets import GoogleDriveWidget, CairoLoadingWidget

from gi.repository import Gtk, Gdk, GLib


class GoogleDriveBrowser(Gtk.Window):

    def __init__(self, *args, **kwargs):
        Gtk.Window.__init__(self, *args, **kwargs)
        self.set_title("GoogleDriveBrowser")
        self.set_size_request(200,200)
        self.set_default_size(600,400)
        self.connect("destroy", Gtk.main_quit)

        self.vbox = Gtk.VBox()
        self.add(self.vbox)

        # waiting screen
        url = GoogleDrive.icon
        loader = CairoLoadingWidget.from_image_url(url)
        loader.set_text(u'connecting to Google Drive\u2122...')
        loader.set_hexpand(True)
        loader.set_vexpand(True)
        self.vbox.add(loader)
        self.loader = loader
        self.show_all()
        print 'GoogleDriveBrowser initialized.'


    def attach_google_drive(self, drive):
        self.gdrive = GoogleDriveWidget(drive)
        self.loader.destroy()
        self.vbox.add(self.gdrive)
        self.show_all()
        return False

    def attach_google_drive_from_oauth(self, secrets):
        print '> authorizing connection...'
        service = get_drive_service(secrets, self.get_title())
        print '> collecting data...'
        drive = GoogleDrive(service)
        print '> loading view...'
        self.attach_google_drive(drive)
        print 'done.'

    def run(self):
        Gtk.main()


