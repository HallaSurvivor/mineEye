#!/usr/bin/env python
import os,os.path
try: from os import getcwdu as getcwd
except ImportError: from os import getcwd
from sys import stdout
thisrep = os.path.dirname(__file__)
imagesrep = os.path.join(thisrep,'images')
try:
    from .lib.PygameReadWrite import reader,form
except ValueError:
    from lib.PygameReadWrite import reader,form
from pygame import *
import subprocess
from platform import system
OS = system().upper()
import imghdr
from io import FileIO

class Lister(reader.Reader):
    
    def __init__(self,liste,pos,size,policesize,fgcolor=(0,0,0),hlcolor=(120,18,250)):
        self.font = os.path.join(thisrep,'MonospaceTypewriter.ttf')
        self.text = ' %s\n'%'\n '.join(liste)
        self.policesize = policesize
        self.fgcolor = fgcolor
        self.hlcolor = hlcolor
        self.foo = -1
        self.pack(pos,size)
        self.scr = display.get_surface()
    
    def pack(self,pos,size):
        width,height = size
        reader.Reader.__init__(self,self.text,pos,width,self.policesize,None,self.font,fgcolor=self.fgcolor,hlcolor=self.hlcolor,split=False)
        self._line = self.foo
        h = self.height
        self.height = height//self.height*self.height
        self.BG = Surface(self.size)
        for i in range(self.height//h): self.BG.fill(0xffffff if i&1 else 0xf0f0f0,(0,i*h,width,h))
    
    def update(self,ev):
        super(Lister,self).update(ev)
        if ev.type == MOUSEBUTTONUP and self.collidepoint(ev.pos):
            self.foo = self.NLINE
        elif ev.type == MOUSEMOTION and ev.buttons[0] and not self.collidepoint(ev.pos):
            self._line = self.foo
    
    @property
    def OUTPUT(self): return None
    @OUTPUT.setter
    def OUTPUT(self,liste):
        self.text = ' %s\n'%'\n '.join(liste)
        reader.Reader.__init__(self,self.text,self.topleft,self.width,self.policesize,self.height,self.font,bg=self.BG,fgcolor=self.fgcolor,split=False,hlcolor=self.hlcolor)
        self._line = self.foo = -1
        
        
    def screen(self):
        super(Lister,self).screen()
        draw.rect(self.scr,(100,100,100),self.inflate(2,2),1)
        draw.lines(self.scr,(0,0,0),0,(self.bottomleft,self.bottomright,self.topright),1)
        
class Button(Rect):
    def __init__(self,image0,image1,image2=None):
        self.scr = display.get_surface()
        self.images = [image0,image1,image2] if image2 else [image0,image1,image0]
        Rect.__init__(self,image0.get_rect())
        self.ACTIV = True
        self.status = False
        self.over = False
        
    def update(self,ev):
        if ev.type == MOUSEMOTION:
            if self.collidepoint(ev.pos) and not self.over:
                self.over = True
                return self.ACTIV
            elif not self.collidepoint(ev.pos) and self.over:
                self.over = False
                return self.ACTIV
        elif ev.type == MOUSEBUTTONUP and ev.button == 1 and self.collidepoint(ev.pos) and self.ACTIV:
            self.status = True
            return True
        elif ev.type == ACTIVEEVENT:
            self.over = False
            return True
        
    def screen(self):
        self.scr.blit(self.images[self.over if self.ACTIV else 2],self)        
        
class Coche(Rect):
    coche0 = image.load(os.path.join(imagesrep,'button0.png'))
    coche1 = image.load(os.path.join(imagesrep,'button1.png'))
    font = font.Font(os.path.join(thisrep,'MonospaceTypewriter.ttf'),8)
    def __init__(self,label=''):
        Rect.__init__(self,Coche.coche0.get_rect())
        self.scr = display.get_surface()
        self.status = False
        label = Coche.font.render(label,1,(255,255,255))
        Rlabel = label.get_rect()
        Rlabel.midleft = self.midright
        self.label = Surface(self.union(Rlabel).size,SRCALPHA)
        self.label.blit(label,Rlabel)
        
    
    def update(self,ev):
        if ev.type == MOUSEBUTTONUP and self.collidepoint(ev.pos):
            self.status ^= 1
            return True
    
    def screen(self):
        self.scr.blit(Coche.coche0 if self.status else Coche.coche1,self)
        self.scr.blit(self.label,self)

class NoCoche:
    
    def __init__(self):
        self.status = False
    def update(self,ev): return False
    def screen(self): pass

class Viewer(Rect):
    
    def __init__(self,pos,size):
        Rect.__init__(self,pos,size)
        self.scr = display.get_surface()
        self.bg = Surface(self.size,SRCALPHA)
        self.IMAGE = None
        self.foo = 0
    
    def __getattribute__(self,_):
        self.corner = Rect(object.__getattribute__(self,'bottomright'),(10,10)).move(-6,-6)
        return object.__getattribute__(self,_)
    
    @property
    def IMAGE(self): return self.image
    @IMAGE.setter
    def IMAGE(self,img):
        self.bg.fill((30,30,30,50))  
        if not img:
            self.image = None
            return
        self.image0 = img
        imgrect = img.get_rect().clamp(self.inflate(-20,-20))
        if self.inflate(-20,-20).contains(imgrect):
            imgrect.center = self.center
            self.image = img
        else:
            imgrect = imgrect.fit(self.inflate(-20,-20))
            self.image = transform.scale(img,imgrect.size)
        r = Rect((imgrect.left-self.left,imgrect.top-self.top),self.IMAGE.get_size())
        self.bg.fill((0,0,0,0),r)
        self.bg.blit(self.IMAGE,r)
        draw.rect(self.bg,(0,0,0),r.inflate(4,4),1)

    def update(self,ev):
        if ev.type == MOUSEMOTION and ev.buttons[0]:
            (x,y),(rx,ry) = ev.pos,ev.rel
            lastpos = x-rx,y-ry
            if self.corner.collidepoint(lastpos):
                self.w += rx
                self.h += ry
                if self.w < 90:
                    self.x += self.w -90
                    self.w = 90
                if self.h < 90:
                    self.y += self.h -90
                    self.h = 90
                self.bg = Surface(self.size,SRCALPHA)
                if self.IMAGE: self.foo = 1
                else:
                    self.bg.fill((30,30,30,50))  
                return True
            elif self.collidepoint(lastpos):
                self.move_ip(ev.rel)
                return True
        elif ev.type == MOUSEBUTTONDOWN and (self.collidepoint(ev.pos) or self.corner.collidepoint(ev.pos)):
            if ev.button == 4:
                self.IMAGE = transform.rotate(self.image0,90)
            elif ev.button == 5:
                self.IMAGE = transform.rotate(self.image0,-90)
            return True
        
    def screen(self):
        if self.foo:
            self.IMAGE = self.image0
            self.foo = 0
        self.scr.blit(self.bg,self)
        r = draw.rect(self.scr,(100,100,100),self,1).inflate(-2,-2)
        draw.lines(self.scr,(0,0,0),0,(r.bottomleft,r.bottomright,r.topright),1)
        self.scr.fill((20,20,20),self.corner)
        draw.rect(self.scr,(150,150,150),self.corner,1)

def foo(self):
    self._index = len(self.OUTPUT)
    self._select = 0,self._index
    self._adjust()
form.Form.set_cursor = property(foo)


class Browser(Rect):
    font0 = font.Font(os.path.join(thisrep,'MonospaceTypewriter.ttf'),8)
    font1 = font.Font(font.get_default_font(),10)
    
    def load_image(self):
        try:
            if os.path.isfile(self.stringpath.OUTPUT) and imghdr.what(self.stringpath.OUTPUT):
                try: self.viewer.IMAGE = image.load(self.stringpath.OUTPUT)
                except:
                    with FileIO(self.stringpath.OUTPUT) as f:
                        f.name = ''
                        self.viewer.IMAGE = image.load(f)
            else: self.viewer.IMAGE = None
        except IOError: self.viewer.IMAGE = None
    
    def __init__(self,path=None,scrsize=(700,420)):
        Rect.__init__(self,(0,0),scrsize)
        self.scr = display.set_mode(self.size,RESIZABLE)
        key.set_repeat(50,50) 
        display.set_caption('Pygame Path Getter') 
        self.stringpath = form.Form((0,0),0,14)
        self.cancel = Button(image.load(os.path.join(imagesrep,"cancel.png")),image.load(os.path.join(imagesrep,"cancel1.png")))
        self.valid = Button(image.load(os.path.join(imagesrep,"valid.png")),image.load(os.path.join(imagesrep,"valid1.png")),image.load(os.path.join(imagesrep,"valid2.png")))
        self.mkdir = Button(transform.scale(image.load(os.path.join(imagesrep,"mkdir.png")),([self.stringpath.height+20]*2)),transform.scale(image.load(os.path.join(imagesrep,"mkdir1.png")),([self.stringpath.height+20]*2)),transform.scale(image.load(os.path.join(imagesrep,"mkdir2.png")),([self.stringpath.height+20]*2)))
        self.showhidden = Coche('hidden files') if OS not in('WINDOWS',) else NoCoche()
        self.showviewer = Coche('preview') 
        self.imagesonly = Coche('images only') 
        self._path = getcwd() if not path or not os.path.isabs(path) else os.path.abspath(path)
        self.stringpath.OUTPUT = os.path.join(self._path,'')
        self.mem = True
        foo = self._path
        while os.path.basename(foo):
            if not os.path.exists(foo): foo = os.path.dirname(foo)
            elif os.path.isfile or os.access(foo,os.W_OK) :
                self.mem = False
                break
        self.folders = Lister([],(0,0),(0,0),14)
        self.files = Lister([],(0,0),(0,0),14)
        self.pack()
        self.viewer = Viewer((0,0),[min(self.folders.size)/2,]*2)
        self.viewer.bottomright = self.folders.bottomright
        self.PATH = self._path
        self.stringpath.set_cursor
    
    def pack(self):
        strpth = self.stringpath.OUTPUT
        foo = self.stringpath._select
        self.stringpath = form.Form((self.left+15,self.top+15),self.width-30,14,maxlines=1,fgcolor=(255,255,255),bg=(30,30,30))
        self.stringpath.width -= self.stringpath.height+25
        self.stringpath.OUTPUT = strpth
        _,self.stringpath._index = self.stringpath._select = foo
        self.stringpath._adjust()
        self.valid.bottomright = self.width-5,self.bottom-5
        self.cancel.topright = self.valid.left-5,self.valid.top
        self.mkdir.topleft = self.stringpath.right+15,self.top+5
        self.folders.pack((self.left+5,self.stringpath.bottom+15),((self.width-15)/2,self.height-self.valid.height-self.stringpath.height-45))
        self.files.pack((self.folders.right+5,self.stringpath.bottom+15),self.folders.size)
        self.showviewer.center = self.valid.center
        self.showviewer.left = 5
        self.imagesonly.center = self.valid.center
        self.imagesonly.centerx = self.folders.centerx
        self.showhidden.center = self.valid.center
        self.showhidden.right = self.folders.right
        
    def update(self,ev):
        self.valid.update(ev)
        self.cancel.update(ev)
        if self.mkdir.update(ev) and self.mkdir.status and self.mkdir.ACTIV:
            self.mkdir.status = False
            foo = [self._path]
            while os.path.basename(foo[0]):
                foo.insert(0,os.path.dirname(foo[0]))
            for fld in foo:
                if not os.path.exists(fld): os.mkdir(fld)
            strpth = self.stringpath.OUTPUT
            self.PATH = self.PATH
            self.stringpath.OUTPUT = strpth
        if (ev.type == MOUSEMOTION and not any(ev.buttons)) or (self.showviewer.status and self.viewer.update(ev)): return
        if self.showhidden.update(ev) or self.imagesonly.update(ev):
            x = self.stringpath.OUTPUT
            self.PATH = self.PATH
            try:
                self.files._line = self.files.text.splitlines().index(' %s'%os.path.basename(x))
                self.stringpath.OUTPUT = x
            except ValueError:
                self.viewer.IMAGE = None
            self.stringpath.set_cursor
            return
        if self.showviewer.update(ev):
            if self.showviewer.status: self.load_image()
            return
        if ev.type == VIDEORESIZE:
            self.width = ev.w if ev.w >= 550 else 600
            self.height = ev.h if ev.h >=180 else 180
            self.scr = display.set_mode(self.size,RESIZABLE)
            self.pack()
            self.viewer.clamp_ip(self)
            return
        self.folders.update(ev)
        self.files.update(ev)
        if ev.type == MOUSEBUTTONUP and ev.button == 1:
            if self.folders.collidepoint(ev.pos):
                if self.folders.LINE:
                    if self.showviewer.status: self.viewer.IMAGE = None
                    if self.folders.LINE == ' ..':
                        self.PATH = os.path.dirname(self.PATH)
                    elif not self.protect:
                        self.PATH = os.path.join(self.PATH,self.folders.LINE[1:])
                    self.stringpath.set_cursor
            elif self.files.collidepoint(ev.pos) and not self.protect:
                self.stringpath.OUTPUT = os.path.join(self.PATH,self.files.LINE[1:])
                self.stringpath.set_cursor
                if self.showviewer.status: self.load_image()
        x = self.stringpath.OUTPUT
        
        if ev.type == KEYDOWN and ev.key == K_TAB:
            bar = ' %s'%os.path.basename(self.stringpath.OUTPUT)
            foo = [i[1:] for i in (self.folders.text+self.files.text).splitlines() if i.startswith(bar)]
            self.stringpath.OUTPUT = os.path.join(self.PATH,os.path.commonprefix(foo))
            if len(foo) == 1 and os.path.isdir(self.stringpath.OUTPUT):
                self.stringpath.OUTPUT = os.path.join(self.stringpath.OUTPUT,'')
            self.stringpath.set_cursor                   
            
        else: self.stringpath.update(ev)
        if x != self.stringpath.OUTPUT:
            if os.path.dirname(x) != os.path.dirname(self.stringpath.OUTPUT):
                x = self.stringpath.OUTPUT
                self.PATH = os.path.dirname(self.stringpath.OUTPUT)
                self.stringpath.OUTPUT = x
                self.viewer.IMAGE = None
            if not os.path.isdir(self.stringpath.OUTPUT):
                try: self.files._line = self.files.text.splitlines().index(' %s'%os.path.basename(self.stringpath.OUTPUT))
                except ValueError: self.files._line = -1
                if self.showviewer.status: self.load_image()

    def show(self):
        self.scr.fill((200,200,200),self)
        r = self.scr.fill((30,30,30),self.stringpath.inflate(20,20))
        draw.rect(self.scr,(100,100,100),r.inflate(2,2),1)
        draw.lines(self.scr,(0,0,0),0,(r.bottomleft,r.bottomright,r.topright),1)
        
        r = Rect(5,self.folders.bottom+5,self.right-10,self.bottom-self.folders.bottom-10)
        self.scr.fill((30,30,30),r)
        draw.rect(self.scr,(100,100,100),r.inflate(2,2),1)
        draw.lines(self.scr,(0,0,0),0,(r.bottomleft,r.bottomright,r.topright),1)
        
        draw.rect(self.scr,(0,0,0),self,1)
        self.stringpath.screen()
        self.folders.screen()
        self.files.screen()
        if self.showviewer.status: self.viewer.screen()
        self.showhidden.screen()
        self.showviewer.screen()
        self.imagesonly.screen()
        self.valid.screen()
        self.cancel.screen()
        self.mkdir.screen()
        display.update(self)
    
    @property
    def PATH(self):
        return self._path
    @PATH.setter
    def PATH(self,value):
        self._path = value
        self.protect = False
        d,f = [],[]
        try: listdir = os.listdir(self._path)
        except OSError as e:
            self.protect = True
            self.folders.OUTPUT = ['..',os.path.basename(self._path)]
            if e.errno == 13:
                self.files.OUTPUT = ['','ACCESS DENIED']
            elif e.errno in (2,20):
                self.files.OUTPUT = ['','FOLDER DOES NOT EXIST']
        else:
            try:
                for i in sorted(listdir,key=lambda x: x.lower()):
                    if self.showhidden.status or not i.startswith('.'):
                        if os.path.isdir(os.path.join(self._path,i)): d.append(i)
                        elif not self.imagesonly.status: f.append(i)
                        else:
                            try:
                                if imghdr.what(os.path.join(self._path,i)) or type(image.load(os.path.join(self._path,i))) is Surface: f.append(i)
                            except: continue
            except UnicodeDecodeError:
                self.protect = True
                self.folders.OUTPUT = ['..',os.path.basename(self._path)]
                self.files.OUTPUT = ['','IT SEEMS THAT THIS FOLDER CONTAINS','SOME MISFORMATTED FILENAMES']
            else:
                d.insert(0,'..')
                self.folders.OUTPUT = d
                self.files.OUTPUT = f
                if self.stringpath.OUTPUT != os.path.join(self._path,''):
                    self.stringpath.OUTPUT = os.path.join(self._path,'')
        if os.path.exists(self._path):
            self.mkdir.ACTIV = False
            self.mem = False if not os.access(self._path,os.W_OK) or os.path.isfile(self._path) else True
        else: self.mkdir.ACTIV = self.mem and True
    
    @property
    def OUTPUT(self): return self.stringpath.OUTPUT
        
def get(path='',mode=None):
    if not mode in (1,2): mode = None
    args = ["python", __file__,path,str(mode)]
    return subprocess.Popen(args,stdout=subprocess.PIPE).communicate()[0].strip()

if __name__ == '__main__':
    import sys
    try: path,mode = sys.argv[1],eval(sys.argv[2])
    except:
        mode = None
        try: path = sys.argv[1]
        except: path = ''
    aaa = Browser(path)
    aaa.valid.ACTIV = False if mode == 1 else True
    aaa.show()
    run = True
    timer = time.Clock()
    while run:
        timer.tick(30)
        aaa.show()
        
        for ev in [event.wait()]+event.get():
            aaa.update(ev)
            if os.path.isabs(aaa.OUTPUT):
                if mode == 2 and os.path.basename(aaa.OUTPUT): aaa.valid.ACTIV = False
                elif mode == 1 and not os.path.basename(aaa.OUTPUT): aaa.valid.ACTIV = False
                else: aaa.valid.ACTIV = True
            
                if ev.type == KEYDOWN and ev.key in (K_RETURN,K_KP_ENTER) or aaa.valid.status:
                    if mode == None or (mode == 1 and os.path.basename(aaa.OUTPUT)) or (mode == 2 and not os.path.basename(aaa.OUTPUT)):
                        stdout.write(aaa.OUTPUT)
                        run = False
                        break
            
            else: aaa.valid.ACTIV = False
                
            if (ev.type == KEYDOWN and ev.key == K_ESCAPE) or aaa.cancel.status or ev.type == QUIT:
                stdout.write('')
                run = False
                break
        
    display.quit()
