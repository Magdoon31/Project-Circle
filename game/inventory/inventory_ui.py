import pygame

class Inventory_ui:
    def __init__(self, screen, inventory, sfx):
        self.screen = screen
        self.inventory = inventory
        self.selected_slot = None
        self.slot_size = self.screen.get_height()//9
        self.columns = 4
        self.padding = 20
        self.slots = []
        self.buttons = []
        self.grid_start_x = self.screen.get_width()//1.4 - self.slot_size*2
        self.grid_start_y = self.screen.get_height()//2.5 - self.slot_size*2
        self.tooltip_start = (self.screen.get_width()//1.84, self.screen.get_height()//1.5)
        self.font_light = {"small" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",18),
                           "mid" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",36),
                           "large" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",64)}
        self.font_heavy = {"small" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",18),
                           "mid" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",36),
                           "large" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",64)}

        self.sfx = sfx
        self.sfx.load_sfx("use", "assets/sfx/UI/use.wav")
        self.sfx.load_sfx("click", "assets/sfx/UI/click1.wav")

    def draw(self):
        self.screen.fill((200, 200, 120))
        self.slots = []
        self.buttons = []
    #rendering slot grid
        for i in range(self.columns):
            for j in range(self.columns):
                slot = pygame.Rect(
                    (self.screen.get_width()//1.4)+self.slot_size*(j-2)+self.padding*(j-2),
                    (self.screen.get_height()//2.5)+self.slot_size*(i-2)+self.padding*(i-2),
                    self.slot_size
                    ,self.slot_size
                    )
                self.slots.append(slot)
                if self.selected_slot == (i,j):
                    pygame.draw.rect(self.screen,(100,255,100),slot,0,5)
                else:
                    pygame.draw.rect(self.screen,(255,255,255),slot,0,5)

    # rendering items
        for i, item in enumerate(self.inventory.items):
            row = i // self.columns
            column = i % self.columns

            x = self.grid_start_x + column * self.slot_size + self.padding*(column-2)+self.screen.get_height()//160
            y = self.grid_start_y + row * self.slot_size + self.padding*(row-2)+self.screen.get_height()//160
            self.screen.blit(item.img,(x,y))


        back_btn_rect = pygame.Rect(self.screen.get_width() - self.screen.get_width()//6,
                        self.screen.get_height()//30,
                        self.screen.get_width()//7,
                        self.screen.get_height()//20
                        )
        self.buttons.append(back_btn_rect)
        pygame.draw.rect(self.screen,(255,255,255),back_btn_rect,0,5)
        back_btn_text = self.font_heavy["mid"].render("Back",True,(0,0,0))
        self.screen.blit(back_btn_text,(back_btn_rect.x+back_btn_rect.width/2-back_btn_text.get_width()/2,back_btn_rect.y+back_btn_rect.height/2-back_btn_text.get_height()/2))

        
        weapon_slot = pygame.Rect(
                            self.screen.get_width()//4,
                            self.screen.get_height()//6,
                            self.slot_size
                            ,self.slot_size
                            )
        self.slots.append(weapon_slot)
        if self.selected_slot == (4,0):
            pygame.draw.rect(self.screen,(100,255,100),weapon_slot,0,5)
        else:
            pygame.draw.rect(self.screen,(255,255,255),weapon_slot,0,5)
        if self.inventory.active_weapon:
            self.screen.blit(self.inventory.active_weapon.img,(weapon_slot.left+self.screen.get_height()//160,weapon_slot.top+self.screen.get_height()//160))
        weapon_slot_text = self.font_heavy["large"].render("Weapon:",True,(255,255,255))
        self.screen.blit(weapon_slot_text,(weapon_slot.left-weapon_slot_text.get_width()*1.1,weapon_slot.top+self.screen.get_height()//100))
        

        armor_slot = pygame.Rect(
                            self.screen.get_width()//4,
                            (self.screen.get_height()//6)*2.5,
                            self.slot_size
                            ,self.slot_size
                            )
        self.slots.append(armor_slot)
        if self.selected_slot == (4,1):
            pygame.draw.rect(self.screen,(100,255,100),armor_slot,0,5)
        else:
            pygame.draw.rect(self.screen,(255,255,255),armor_slot,0,5)
        if self.inventory.active_armor:
            self.screen.blit(self.inventory.active_armor.img,(armor_slot.left+self.screen.get_height()//160,armor_slot.top+self.screen.get_height()//160))
        armor_slot_text = self.font_heavy["large"].render("Armor:",True,(255,255,255))
        self.screen.blit(armor_slot_text,(armor_slot.left-armor_slot_text.get_width()*1.1,armor_slot.top+self.screen.get_height()//100))


        trinket_slot = pygame.Rect(
                            self.screen.get_width()//4,
                            (self.screen.get_height()//6)*4,
                            self.slot_size
                            ,self.slot_size
                            )
        self.slots.append(trinket_slot)
        if self.selected_slot == (4,2):
            pygame.draw.rect(self.screen,(100,255,100),trinket_slot,0,5)
        else:
            pygame.draw.rect(self.screen,(255,255,255),trinket_slot,0,5)
        if self.inventory.active_trinket:
            self.screen.blit(self.inventory.active_trinket.img,(trinket_slot.left+self.screen.get_height()//160,trinket_slot.top+self.screen.get_height()//160))
        trinket_slot_text = self.font_heavy["large"].render("Trinket:",True,(255,255,255))
        self.screen.blit(trinket_slot_text,(trinket_slot.left-trinket_slot_text.get_width()*1.1,trinket_slot.top+self.screen.get_height()//100))


        tooltip_rect = pygame.Rect(
                            self.tooltip_start[0],
                            self.tooltip_start[1],
                            self.screen.get_width()//3,
                            self.screen.get_height()//4.8)
        pygame.draw.rect(self.screen,(220,220,220),tooltip_rect,0,10)
        if self.inventory.selected_item:
            self.tooltip_text = {"Name" : self.font_heavy["small"].render(f"{self.inventory.selected_item.name}",True,(0,0,0)),
                                "Type" : self.font_light["small"].render(f"Type: {self.inventory.selected_item.type}",True,(0,0,0)),
                                "desc" : self.font_light["small"].render(f"{self.inventory.selected_item.description}",True,(50,50,50))
                                }
            self.screen.blit(self.tooltip_text["Name"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60))
            self.screen.blit(self.tooltip_text["Type"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+self.tooltip_text["Name"].get_height()))
            self.screen.blit(self.tooltip_text["desc"],(tooltip_rect.left+tooltip_rect.width//3.6,tooltip_rect.top+self.screen.get_height()//60))

        
            if self.inventory.selected_item.type == "weapon":

                self.tooltip_text["Damage"] = self.font_light["small"].render(f"DMG: {self.inventory.selected_item.damage}",True,(80,10,10))
                self.tooltip_text["Fire Rate"] = self.font_light["small"].render(f"Fire Rate: {self.inventory.selected_item.rate_of_fire}",True,(10,80,10))
                self.tooltip_text["Range"] = self.font_light["small"].render(f"Range: {self.inventory.selected_item.range}",True,(10,80,10))

                self.screen.blit(self.tooltip_text["Damage"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+28*2))
                self.screen.blit(self.tooltip_text["Fire Rate"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+28*3))
                self.screen.blit(self.tooltip_text["Range"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+28*4))
                
            elif self.inventory.selected_item.type == "armor":

                self.tooltip_text["Health"] = self.font_light["small"].render(f"Bonus HP: {self.inventory.selected_item.bonus_hp}",True,(80,10,10))
                self.tooltip_text["Defense"] = self.font_light["small"].render(f"DEF: {self.inventory.selected_item.defense}",True,(10,10,80))

                self.screen.blit(self.tooltip_text["Health"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+28*2))
                self.screen.blit(self.tooltip_text["Defense"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+28*3))

            self.tooltip_text["Effect"] = self.font_light["small"].render(f"Effect: {self.inventory.selected_item.effect_description}",True,(130,40,110))
            self.screen.blit(self.tooltip_text["Effect"],(tooltip_rect.left+tooltip_rect.width//3.6,tooltip_rect.top+self.screen.get_height()//60+self.tooltip_text["desc"].get_height()))

        equip_btn_rect = pygame.Rect(self.screen.get_width()//1.8,
                        self.screen.get_height()//1.12,
                        self.screen.get_width()//7,
                        self.screen.get_height()//20)
        remove_btn_rect = pygame.Rect(self.screen.get_width()//1.8+equip_btn_rect.width*1.1,
                        self.screen.get_height()//1.12,
                        self.screen.get_width()//7,
                        self.screen.get_height()//20)
        if self.inventory.selected_item is not None:
            equip_btn_text = self.font_heavy["mid"].render("Unequip" if self.inventory.selected_item in self.inventory.active_items.values() else "Equip",True,(0,0,0))
            self.buttons.append(equip_btn_rect)
            pygame.draw.rect(self.screen,(230,140,100) if self.inventory.selected_item in self.inventory.active_items.values() else (120,230,110),equip_btn_rect,0,5)
            self.screen.blit(equip_btn_text,(equip_btn_rect.left+equip_btn_rect.width//2-equip_btn_text.get_width()//2,
                                                     equip_btn_rect.top+equip_btn_rect.height//2-equip_btn_text.get_height()//2))
            remove_btn_text = self.font_heavy["mid"].render("Remove",True,(0,0,0))
            self.buttons.append(remove_btn_rect)
            pygame.draw.rect(self.screen,(230,140,100),remove_btn_rect,0,5)
            self.screen.blit(remove_btn_text,(remove_btn_rect.left+remove_btn_rect.width//2-remove_btn_text.get_width()//2,
                                                     remove_btn_rect.top+remove_btn_rect.height//2-remove_btn_text.get_height()//2))
            
           
        
        

    def handle_click(self, pos, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, slot in enumerate(self.slots):
                    if slot.collidepoint(pos):

                        row = i // self.columns
                        column = i % self.columns

                        if self.selected_slot == (row,column):
                            self.selected_slot = None
                            self.inventory.selected_item = None
                            self.sfx.play("click")
                        else:
                            self.selected_slot = (row,column)

                            if self.selected_slot == (4,0):
                                self.inventory.selected_item = self.inventory.active_weapon
                            elif self.selected_slot == (4,1):
                                self.inventory.selected_item = self.inventory.active_armor
                            elif self.selected_slot == (4,2):
                                self.inventory.selected_item = self.inventory.active_trinket
                            elif len(self.inventory.items) >= i + 1:
                                self.inventory.selected_item = self.inventory.items[i]
                            else:
                                self.inventory.selected_item = None
                            self.sfx.play("click")
   
                        print(self.inventory.selected_item.name if self.inventory.selected_item else None, [item.name if item else None for item in self.inventory.active_items.values()])
                for i, btn in enumerate(self.buttons):
                    if btn.collidepoint(pos):
                        self.sfx.play("use")
                        if i == 0:
                            return "map"
                        elif i == 1:
                            if self.inventory.selected_item in self.inventory.active_items.values():
                                self.inventory.unequip_item(self.inventory.selected_item)
                                self.selected_slot = None
                            elif self.inventory.selected_item:
                                self.inventory.equip_item(self.inventory.selected_item)
                                self.selected_slot = None
                        elif i == 2:
                            if self.inventory.selected_item in self.inventory.active_items.values():
                                if self.inventory.selected_item.type == "weapon":
                                    self.inventory.active_weapon = None
                                    self.inventory.active_items["weapon"] = None
                                elif self.inventory.selected_item.type == "armor":
                                    self.inventory.active_armor = None
                                    self.inventory.active_items["armor"] = None
                                elif self.inventory.selected_item.type == "trinket":
                                    self.inventory.active_trinket = None
                                    self.inventory.active_items["trinket"] = None
                                self.inventory.selected_item = None
                                self.selected_slot = None
                            elif self.inventory.selected_item:
                                self.inventory.remove_item(self.inventory.selected_item)
                                self.inventory.selected_item = None
                                self.selected_slot = None

