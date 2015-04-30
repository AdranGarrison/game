__author__ = 'Alan'





            if 'bruise' in self.layers[i].damagetype:
                if pressure>self.layers[i].material.tensile_strength*500000:
                    if self.layers[i].plural==False:
                        print("the {}'s {} is bruised".format(self.name,self.layers[i].name))
                    else:
                        print("the {}'s {} are bruised".format(self.name,self.layers[i].name))
                    severity=pressure/(self.layers[i].material.tensile_strength*500000)-1
                    pythagoreanseverity=(severity**2+self.layers[i].damage['bruise']**2)**0.5
                    self.layers[i].damage['bruise']=pythagoreanseverity
                    print(self.layers[i].damage['bruise'])

            if 'crack' in self.layers[i].damagetype:
                print(force)
                if force>15*(3.14*self.layers[i].material.tensile_strength*1000000*self.layers[i].thickness**3)/self.layers[i].length:
                    if self.layers[i].plural==False:
                        print("the {}'s {} is cracked".format(self.name,self.layers[i].name))
                    else:
                        print("the {}'s {} are cracked".format(self.name,self.layers[i].name))
                    severity=force/((15*3.14*self.layers[i].material.tensile_strength*1000000*self.layers[i].thickness**3)/self.layers[i].length)-1
                    self.layers[i].damage['crack']+=severity
                    print(self.layers[i].damage['crack'])

            if 'dent' in self.layers[i].damagetype:
                pass

            if 'break' in self.layers[i].damagetype:
                pass

            if 'bend' in self.layers[i].damagetype:
                pass

            if 'cut' in self.layers[i].damagetype:
                pass

            if 'shatter' in self.layers[i].damagetype:
                pass

            if 'crush' in self.layers[i].damagetype:
                pass



