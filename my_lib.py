import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
import os
import pymupdf
import unicodedata

df_content = pd.read_csv("data/df_student_content.csv")

class Config:
    pass
config = Config()
config.WIDTH = 595
config.HEIGHT = 842
config.INNER_SEP = 7
config.name = f"Computing Expo '24"
config.draw_background = 1
config.draw_border = 1
config.draw_internal_borders = 0

CM_TO_PTS = 28.3465
to_pts = lambda x: x*CM_TO_PTS
to_cm = lambda x: x/CM_TO_PTS

#
# company logo functions and data
#

# loading images a pixmap results in a 515MB vs 85 MB for stream load
# but pixmap is faster to load and allows scaling 
# => will scale logos in Makefile before copying to logos/ folder 
def load_logo(company, mode='stream', debug=False):
    for ext in ['jpeg', 'png']:
        filename = f"logos/{company}.{ext}".replace(" ", "_")
        if os.path.exists(filename):
            if mode=='stream':
                image = open(filename, "rb").read()
            elif mode=='pixmap':
                image = pymupdf.Pixmap(filename)
                if debug: print (f"Loaded {company} with pixmap height {image.height}")
                # image.shrink()
            return image 

    return None

companies = {
    'wit.ie': 'SETU',
    'setu.ie': 'SETU',
    'postgrad.wit.ie': 'SETU',
    'mail.wit.ie': 'SETU',
    'ofoghlu.net': 'Google',
    'redhat.com': 'Red Hat',
    'waltoninstitute.ie': 'Walton Institute',
    'brickfield.ie': 'Brickfield',
    'scurri.com': 'Scurri',
    'kargo.com': 'Kargo',
    'wlrfm.com': 'WLR FM',
    'jaguarlandrover.com': 'Jaguar Land Rover',
    'sunlife.com': 'Sun Life',
    'sra.io': 'Security_Risk_Advisors',
    'dataworks.ie': 'dataworks',
    'unum.com': 'Unum',
    'specialisterne.com': 'Specialisterne',
    'ukg.com': 'UKG',
    'engagexr.com': 'Engage XR',
    'sanofi.com': 'Sanofi',
    'amlhq.com': 'AML HQ',
    'portofwaterford.com': 'Port of Waterford',
    'playerstatdata.com': 'PlayerStat Data',
    'live.ie': 'Live',
    'kilderry.ie': 'Kilderry',
}

# REMEMBER to load images at most once per company we use xref parameter


def update_config(config, width, height, left, top):
    config.width = to_pts(width)
    config.height = to_pts(height)
    config.left = to_pts(left)
    config.bottom = to_pts(top)    
    config.rows = int((config.HEIGHT-config.bottom)//config.height)
    config.cols = int((config.WIDTH-config.left)//config.width)
    config.n = config.rows * config.cols
    config.right = config.WIDTH - config.left - config.cols*config.width
    config.top = config.HEIGHT - config.bottom - config.rows*config.height


# def draw_layout(config):

#     fig, ax = plt.subplots(figsize=(config.WIDTH, config.HEIGHT))
#     ax.set_xlim(0, config.WIDTH)
#     ax.set_ylim(0, config.HEIGHT)
#     ax.set_aspect('equal')
#     ax.axis('off')

#     rows = int(np.floor((config.HEIGHT - config.top) / config.height))
#     cols = int(np.floor((config.WIDTH - config.left) / config.width))

#     rectangles = []
#     text = f"Layout\n{to_cm(config.width):.1f}x{to_cm(config.height):.1f}+{to_cm(config.left):.1f}+{to_cm(config.top):.1f}"
#     for col in range(cols):
#         x = config.left + c*config.width
#         for r in range(rows):
#             y = config.HEIGHT - config.top - config.height - r*config.height
#             rect = patches.Rectangle((x, y), config.width, config.height, linewidth=1, edgecolor='b', facecolor='none')
#             ax.add_patch(rect)
#             ax.text(x+config.width/2, y+config.height/2, text, ha='center', va='center', fontsize=4)

#     # crop marks
#     bottom = config.HEIGHT - config.top - rows*config.height
#     right = config.WIDTH - config.left - cols*config.width
#     for c in range(cols+1):
#         x = config.left + c*config.width
#         ax.plot([x,x], [0, bottom/2], 'k-', lw=1)
#         ax.plot([x,x], [config.HEIGHT-config.top/2, config.HEIGHT], 'k-', lw=1)
#     for r in range(rows+1):
#         y = config.HEIGHT - config.top - r*config.height
#         ax.plot([0, config.left/2], [y,y], 'k-', lw=1)
#         ax.plot([config.WIDTH-right/2, config.WIDTH], [y,y], 'k-', lw=1)

#     rect = patches.Rectangle((0,0), config.WIDTH, config.HEIGHT, linewidth=1, edgecolor='r', facecolor='none')
#     ax.add_patch(rect)

#     return fig, (rows,cols)


#
# data functions
#


def clean_name_df(df, drop_duplicates=True):
    columns = ['First Name', 'Surname', 'Email', 'Ticket Type']
    df = df[columns].fillna("")
    if drop_duplicates: df = df.drop_duplicates()
    df.columns = ['Firstname', 'Surname', 'Email', 'Type']
    #criteria = df.Email.astype(str).str.count("@")==1 loc[criteria]
    df = df.reset_index(drop=True)
    return df


def get_domain_and_company(df_row):
    email = df_row.Email
    if email.count("@")!=1:
        return email, None
    domain = email.split('@')[1]
    if df_row.Type in ['Student Attendees', 'SETU Staff']: 
        domain = "setu.ie"
    company = companies.get(domain.lower(), None)

    return domain, company

#
# PDF generation
#

def get_rc(config, idx):
    """Return the row and column of the idx-th label on the page."""
    on_page = idx % (config.n)
    row = on_page // config.cols
    col = on_page % config.cols

    return row, col

def draw_cut_lines(config, page, page_label, message="When printing, ensure 'Actual size' or (100% scale) is selected."):
        
        c = config
        cut_lines = page.new_shape()
        for row in range(c.rows+1):
            y = c.HEIGHT - c.top - row*c.height
            cut_lines.draw_line((0,y), (c.left/2,y))
            cut_lines.draw_line((c.WIDTH,y), (c.WIDTH-c.right/2,y))
        for col in range(c.cols+1):
            x = c.left + col*c.width
            cut_lines.draw_line((x,0), (x,c.bottom/2))
            cut_lines.draw_line((x,c.HEIGHT-c.top/2), (x,c.HEIGHT))
        cut_lines.finish(color=(0, 0, 0))
        cut_lines.commit()
        page_number = page.new_shape()
        page_number.insert_text((c.WIDTH-60, c.top/2), page_label, fontsize=8, fontname="Helvetica-Bold", color=(0,0,0))

        if message:
            page_number.insert_text((1.2*c.left, c.top/4), message, fontsize=12, fontname="Helvetica-Bold", color=(1,0,0))
        page_number.finish()
        page_number.commit()


def draw_project_info(page, x, y, number, room):
    width, height = 170, 30  # size needed for longest label 
    project_label = f"#{int(number)} / {room.replace('TL2','TL2.')}"
    project_frame = page.new_shape()
    x0, y0 = x + (config.width-width)/2, y+(60+config.height-height)/2
    rect = (x0, y0, x0+width, y0+height)
    project_frame.draw_rect(rect, radius=.1)
    project_frame.finish(fill=(0.3,0.3,0.3), color=(1, 1, 1))
    project_frame.commit()
    #
    project = page.new_shape()
    y0 += 4 # lower text a bit 
    rect = (x0, y0, x0+width, y0+height)
    project.insert_textbox(rect, project_label, fontsize=16, fontname="Helvetica-Bold", align=1, stroke_opacity=1, fill=(1,1,1), color=(1,1,1))
    project.finish(color=(1, 1, 1))
    project.commit()

def draw_company_info(page, x, y, company, domain, logo_cache, debug=False):

    # load logo if not already loaded
    if company not in logo_cache:
        logo_cache[company] = {'xref':0,'image': load_logo(company)}
        if debug: print(f"Loaded logo for '{company}'")

    x0, y0 = x+config.INNER_SEP, y+70          
    rect = (x0,y0, x+config.width-config.INNER_SEP, y+config.height-config.INNER_SEP)
    #
    logo_frame = page.new_shape()
    if config.draw_internal_borders:
        logo_frame = page.new_shape()
        logo_frame.draw_rect(rect, radius=.1)
    if logo_cache[company]['image'] is not None:
        logo_cache[company]['xref'] = page.insert_image(rect, 
            stream=logo_cache[company]['image'], 
            xref=logo_cache[company]['xref']
        )
        if debug: print(company, logo_cache[company]['xref'])
    else:
        for fontsize in range(20, 10, -1):
            result = logo_frame.insert_textbox(rect, company or domain, fontsize=fontsize, fontname="Helvetica-Bold", align=1, stroke_opacity=0.5, fill=(1,0,1), color=(0,0,0))
            if result>=0: 
                if debug: print(f"Used fontsize {fontsize} for COMPANY {config.name}")
                break    
    logo_frame.finish(color=(0, 0, 0))
    logo_frame.commit()


def generate_doc(df, config, first_page_only=False, debug=False):

    background = open("logos/background.png", "rb").read()
    background_xref = 0
    setu_logo = load_logo("SETU")
    setu_logo_xref = 0

    logo_cache = {}

    doc = pymupdf.open()
    num_pages = df.shape[0] // (config.rows*config.cols) + 1
    for idx, df_row in df.iterrows():

        # new page ?
        if idx % (config.n) == 0:
            if first_page_only and idx>0: break # first page only for sample
            page = doc.new_page(width=config.WIDTH, height=config.HEIGHT)
            draw_cut_lines(config, page, f"Page {idx//(config.n)+1}/{num_pages}")

        row, col = get_rc(config, idx)

        # badge location

        x = config.left + col*config.width
        y = config.HEIGHT - config.top - (config.rows-row)*config.height

        # background - place image scaled to name label size
        # TODO: scale to correct aspect ratio
        # want a faint background image so can ignore bleed effects?
        if config.draw_background:
            background = open("logos/background.png", "rb").read()
            background_xref = 0
            background_xref = page.insert_image((x,y, x+config.width,y+config.height), stream=background, xref=background_xref)
        
        # border

        if config.draw_border:
            border = page.new_shape()
            border.draw_rect((x,y, x+config.width,y+config.height))
            border.finish(color=(0, 0, 1))
            border.commit()

        # setu logo 
        
        x0, y0 = x+config.INNER_SEP, y+config.INNER_SEP
        aspect = 200/525 # SETU aspect ratio
        setu_width = 65
        rect = (x0, y0, x0+setu_width, y0+setu_width*aspect)
        #
        if config.draw_internal_borders:
            logo_frame = page.new_shape()
            logo_frame.draw_rect(rect, radius=.1)
            logo_frame.finish(color=(0,0,0))
            logo_frame.commit()
        setu_logo_xref = page.insert_image(rect, stream=setu_logo, xref=setu_logo_xref)
        
        # event name
        
        x0, y0 = x+config.INNER_SEP+setu_width+config.INNER_SEP, y+config.INNER_SEP
        rect = (x0, y0, x+config.width-config.INNER_SEP, y0+setu_width*aspect+5)
        #
        expo_name = page.new_shape()
        if config.draw_internal_borders:
            expo_name.draw_rect(rect, radius=.1)
        for fontsize in range(24, 10, -1):
            result = expo_name.insert_textbox(rect, config.name, fontsize=fontsize, fontname="Helvetica-Bold", align=2, stroke_opacity=0.5, fill=(0,0,1), color=(0,0,0))
            if result>=0: 
                if debug: print(f"Used fontsize {fontsize} for {config.name}")
                break        
        expo_name.finish()
        expo_name.commit()    

        # name 

        x0, y0 = x+config.INNER_SEP, y+40
        rect = (x0, y0, x+config.width-config.INNER_SEP, y0+32)
        #
        name_box = page.new_shape()
        name = unicodedata.normalize('NFC', (df_row.Firstname + " " + df_row.Surname))
        if config.draw_internal_borders:
            name_box.draw_rect(rect)
        for fontsize in range(18, 10, -1):
            result = name_box.insert_textbox(rect, name, fontsize=fontsize, fontname="Helvetica-Bold", align=1, stroke_opacity=1, fill=(0,0,1), color=(0,0,0))
            if debug: print(f"Used fontsize {fontsize} for NAME {name}")
            if result>=0: break
        name_box.finish()
        name_box.commit()

        # project info / company logo / domain name
    
        domain, company = get_domain_and_company(df_row)

        if df_row.Type in ['Student Attendees'] and name in df_content.Name.values:

            df_content_row = df_content.loc[df_content.Name==name]
            if df_content_row.shape[0]>1:
                # print(f"Multiple entries found for '{name}'")
                continue

            draw_project_info(page, x, y, df_content_row['Number'].values[0], df_content_row['Room'].values[0])

        else:

            draw_company_info(page, x, y, company, domain, logo_cache)
            
    return doc
