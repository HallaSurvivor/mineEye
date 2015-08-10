# -*- coding: utf-8 -*-
from sys import stdout
import textwrap
import pygame
pygame.font.init()

class Reader(pygame.Rect,object):
    
    class ln(object):
        def __init__(self,string,nl,sp):
            self.string = string
            self.nl = nl
            self.sp = sp

    def __init__(self,text,pos,width,fontsize,height=None,font=None,bg=(250,250,250),fgcolor=(0,0,0),hlcolor=(180,180,200),split=True):
        self._original = text.expandtabs(4).split('\n')
        self.BG = bg
        self.FGCOLOR = fgcolor
        self._line = 0
        self._index = 0
        if not font:
            self._fontname = pygame.font.match_font('mono',1)
            self._font = pygame.font.Font(self._fontname,fontsize)
        elif type(font) == str:
            self._fontname = font
            self._font = pygame.font.Font(font,fontsize)
        self._w,self._h = self._font.size(' ')
        self._fontsize = fontsize
        if not height: pygame.Rect.__init__(self,pos,(width,self._font.get_height()))
        else: pygame.Rect.__init__(self,pos,(width,height))
        self.split = split
        self._splitted = self.splittext()
        self._x,self._y = pos
        self._src = pygame.display.get_surface()
        self._select = self._line,self._index
        self._hlc = hlcolor
        self.HLCOLOR = hlcolor

    def splittext(self):
        nc = self.width // self._w
        out = []
        for e,i in enumerate(self._original):
            a = Reader.ln('',e,0)
            if not i:
                out.append(a)
                continue
            for j in textwrap.wrap(i,nc,drop_whitespace=False) if self.split else [i]:
                out.append(Reader.ln(j,e,a.sp+len(a.string)))
                a = out[-1]
        return out

    @property
    def HLCOLOR(self):
        return self._hlc
    @HLCOLOR.setter
    def HLCOLOR(self,color):
        self._hlsurface = pygame.Surface((self._w,self._h),pygame.SRCALPHA)
        self._hlsurface.fill(color)

    @property
    def POS(self):
        return self._line,self._index

    @property
    def NLINE(self):
        return self._splitted[self._line].nl

    @property
    def LINE(self):
        return self._original[self.NLINE]
        
    @property
    def WORD(self):
        try:
            s = self._splitted[self._line].sp+self.wrd
            p1 = self.LINE[:s].split(' ')[-1]
            p2 = self.LINE[s:].split(' ')[0]
            if p2: return p1+p2
        except: return None
    
    @property
    def SELECTION(self):
        p1,p2 = sorted(((self._line,self._index),self._select))
        if p1 != p2:
            selection = [len(i.string) for i in self._splitted[:p2[0]]]
            return '\n'.join(self._original)[sum(selection[:p1[0]]) + self._splitted[p1[0]].nl + p1[1]:sum(selection) + self._splitted[p2[0]].nl + p2[1]]
        return ''
                
    @property
    def FONTSIZE(self):
        return self._fontsize
    @FONTSIZE.setter
    def FONTSIZE(self,size):
        self._font = pygame.font.Font(self._fontname,size)
        self._fontsize = size
        self._w,self._h = self._font.size(' ')
        self._splitted = self.splittext()
        y = self._y
        h = len(self._splitted) * self._h
        if h > self.height:
            if self._y - self._h < self.bottom - h: self._y = self.bottom - h
        self._y += (self.top - self._y)%self._h
        self.HLCOLOR = self._hlc
    
    def screen(self):
        clip = self._src.get_clip()
        self._src.set_clip(self.clip(clip))
        try: self._src.fill(self.BG,self)
        except: self._src.blit(self.BG,self)
        
        start = (self.top - self._y) // self._h
        end = (self.bottom - self._y) // self._h + 1

        p1,p2 = sorted(((self._line,self._index),self._select))

        y = self._y + start * self._h
        for py,i in enumerate(self._splitted[start:end],start):
            x = self._x
            for px,j in enumerate(i.string):
                if py != self.NLINE:
                    self._src.blit(self._font.render(j,1,self.FGCOLOR),(x,y))
                else:
                    self._font.set_italic(1)
                    self._src.blit(self._font.render(j,1,self.HLCOLOR),(x,y))
                    self._font.set_italic(0)
                x += self._w
            y += self._h
        self._src.set_clip(clip)
        
    def show(self):
        self.screen()
        pygame.display.update(self)
            
    def update(self,ev):

        line,index = self._line,self._index
        ctrl = pygame.key.get_pressed()
        ctrl = ctrl[pygame.K_RCTRL]|ctrl[pygame.K_LCTRL]
        
        def scrollup(n):
            y = self._y
            if self._y + self._h * n > self.top: self._y = self.top
            else: self._y += self._h * n
        
        def scrolldown(n):
            y = self._y
            h = len(self._splitted) * self._h
            if h > self.height:
                if self._y - self._h * n < self.bottom - h: self._y = self.bottom - h
                else: self._y -= self._h * n
        
        if ev.type == pygame.KEYDOWN:            
            if ev.key == pygame.K_UP:
                scrollup(1)
                
            elif ev.key == pygame.K_DOWN:
                scrolldown(1)           
            
            elif ctrl and ev.key == pygame.K_KP_PLUS:
                self.FONTSIZE += 1         
            
            elif ctrl and ev.key == pygame.K_KP_MINUS and self._fontsize:
                self.FONTSIZE -= 1

        elif ev.type == pygame.MOUSEBUTTONDOWN and self.collidepoint(ev.pos):
            if ev.button == 1:
                self._line = (ev.pos[1] - self._y) // self._h
                self._index = (ev.pos[0] - self._x) // self._w
                self.wrd = self._index
                if ((ev.pos[0] - self._x) % self._w) > (self._w // 2): self._index += 1
                if self._line > len(self._splitted)-1:
                    self._line = len(self._splitted)-1
                    self._index = len(self._splitted[self._line].string)
                if self._index > len(self._splitted[self._line].string): self._index = len(self._splitted[self._line].string)
                self._select = self._line,self._index
                
        elif ev.type == pygame.MOUSEBUTTONUP and self.collidepoint(ev.pos):
            try:
                if ev.click[4]: scrollup(sum(range(1,ev.click[4]+1))/10+1)
                elif ev.click[5]: scrolldown(sum(range(1,ev.click[5]+1))/10+1)
            except:
                if ev.button == 4:
                    scrollup(3)
                
                elif ev.button == 5:
                    scrolldown(3)
        
        elif ev.type == pygame.MOUSEMOTION and ev.buttons[0] and self.collidepoint(ev.pos):
            self._line = (ev.pos[1] - self._y) // self._h
            self._index = (ev.pos[0] - self._x) // self._w
            if ((ev.pos[0] - self._x) % self._w) > (self._w // 2): self._index += 1
            if self._line > len(self._splitted)-1:
                self._line = len(self._splitted)-1
                self._index = len(self._splitted[self._line].string)
            if self._index > len(self._splitted[self._line].string): self._index = len(self._splitted[self._line].string)
