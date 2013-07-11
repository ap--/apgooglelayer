
from gi.repository import Gtk, GdkPixbuf
import array
import dateutil.parser
import dateutil.tz
import requests
import StringIO
from PIL import Image
import cairo

class GoogleDriveWidget(Gtk.VBox):

    def __init__(self, drive, *args, **kwargs):
        super(GoogleDriveWidget, self).__init__(*args, **kwargs)

        self._cache = {}
        self.drive = drive
        self.treeview = Gtk.TreeView()
        treestore = drive.folder_structure_as_gtktreestore(
                        fields='items(id,mimeType,modifiedDate,title,iconLink,labels/*)')
        self.treeview.set_model(treestore)
        def sort_by_title(model, row1, row2, userdata):
            col, _ = model.get_sort_column_id()
            v1 = model.get_value(row1, col)['title']
            v2 = model.get_value(row2, col)['title']
            if v1 < v2:
                return -1
            elif v1 == v2:
                return 0
            else:
                return 1
        self.treeview.get_model().set_sort_func(0, sort_by_title, None)
        self.treeview.get_model().set_sort_column_id(0,Gtk.SortType.ASCENDING)
        self._append_columns()
        #self._append_text_column('miau', 'mimeType')
        
        select = self.treeview.get_selection()
        select.set_mode(Gtk.SelectionMode.BROWSE)
        select.connect("changed", self.on_tree_selection_changed)
        select.unselect_all()

        #self.set_enable_tree_lines(True)
        #self.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)

        scroll = Gtk.ScrolledWindow()
        scroll.add(self.treeview)

        self.add(scroll)

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            pass

    def _append_columns(self):
        # icon stuff
        column = Gtk.TreeViewColumn(self.drive.user['name'])
        column.set_alignment(0.0)
        column.set_expand(True)
        cell = Gtk.CellRendererText()
        icon = Gtk.CellRendererPixbuf()
        column.pack_start(icon, False)
        column.pack_start(cell, False)
        column.set_cell_data_func(icon, self.get_datatype)
        column.set_cell_data_func(cell, self.get_datainfo)
        self.treeview.append_column(column)

        # starred
        column = Gtk.TreeViewColumn('')
        pb = Gtk.CellRendererPixbuf()
        column.pack_start(pb, False)
        column.set_cell_data_func(pb, self.get_starred)
        self.treeview.append_column(column)
        
        # picture
        column = Gtk.TreeViewColumn('owner')
        pb = Gtk.CellRendererPixbuf()
        column.pack_start(pb, False)
        column.set_cell_data_func(pb, self.get_ownerpic)
        self.treeview.append_column(column)

        # LastModified
        self._append_text_column('lastModified', 'modifiedDate', convfun=lambda x: dateutil.parser.parse(x).astimezone(dateutil.tz.gettz()).strftime('%a %b %d %H:%M:%S'))


    def get_starred(self, column, cell, model, iter, data):
        isStarred = model.get_value(iter, 0)['labels']['starred']
        url = ['http://ssl.gstatic.com/ui/v1/star/star-hover4.png',
               'http://ssl.gstatic.com/ui/v1/star/star-lit-hover4.png'][isStarred]
        cell.set_property('pixbuf',self._url_to_pixbuf(url))

    def _url_to_pixbuf(self, url, scale=(16,16)):
        try:
            pb = self._cache[url]
        except KeyError:
            pl = GdkPixbuf.PixbufLoader()
            img = requests.get(url).content
            pl.write(img)
            pl.close()
            pb = pl.get_pixbuf()
            if scale:
                pb = pb.scale_simple(scale[0],scale[1],GdkPixbuf.InterpType.BILINEAR)
            self._cache[url] = pb
        return pb

    def _append_text_column(self, columntitle, drivefilekey, convfun=(lambda x:x)):
        column = Gtk.TreeViewColumn(columntitle)
        cell = Gtk.CellRendererText()
        column.pack_start(cell, False)
        def display(column, cell, model, iter, data):
            d = model.get_value(iter,0)[drivefilekey]
            d = convfun(d)
            cell.set_property('text', d)
        column.set_cell_data_func(cell, display)
        self.treeview.append_column(column)
    
    def get_lastmod(self, column, cell, model, iter, data):
        date = model.get_value(iter, 0)['modifiedDate']
        dtime = dateutil.parser.parse(date)                
        s = dtime.astimezone(dateutil.tz.gettz()).strftime('%a %b %d %H:%M:%S')
        cell.set_property('text', s)
        
    def get_ownerpic(self, column, cell, model, iter, data):
        cell.set_property('pixbuf', self._url_to_pixbuf(self.drive.user['image']))


    def get_datatype(self, column, cell, model, iter, data):
        ICON = self._url_to_pixbuf(model.get_value(iter, 0)['iconLink'])
        cell.set_property('pixbuf', ICON)

    def get_datainfo(self, column, cell, model, iter, data):
        name = model.get_value(iter, 0)['title']
        cell.set_property('text', name)




def pil_from_url(url):
    imdata = requests.get(url).content
    return Image.open(StringIO.StringIO(imdata))



def cairo_ImageSurface_from_pil(im):
    arr = array.array('B', im.tostring('raw', 'BGRA'))
    narr = array.array('B')
    for r,g,b,a in zip(*[arr[i::4] for i in range(4)]):
        A = a/255.
        narr.extend((int(r*A), int(g*A), int(b*A), a))
    return cairo.ImageSurface.create_for_data(narr,
                cairo.FORMAT_ARGB32, im.size[0], im.size[1])


