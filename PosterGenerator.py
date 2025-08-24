from SpotifyWrapper import SpotifyWrapper
from PosterType import PosterType
from PIL import Image, ImageDraw, ImageFont
import ColorTools

class PosterGenerator:
    def __init__(self):
        try:
            self.title_font = ImageFont.truetype("./JetBrainsMono/JetBrainsMono-Bold.ttf",size=70)
            self.artist_font = ImageFont.truetype("./JetBrainsMono/JetBrainsMono-Regular.ttf",size=60)
            self.info_font = ImageFont.truetype("./JetBrainsMono/JetBrainsMono-Regular.ttf",size=40)
            self.song_font = ImageFont.truetype("./JetBrainsMono/JetBrainsMono-Regular.ttf",size=45)
            self.small_font = ImageFont.truetype("./JetBrainsMono/JetBrainsMono-Regular.ttf",size=25)
        except:
            self.title_font = ImageFont.load_default()
            self.artist_font = ImageFont.load_default()
            self.info_font = ImageFont.load_default()
            self.song_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()

    def __add_cover(self,poster,sw:SpotifyWrapper,ptype:PosterType, album):
        cover_size = ptype.width-2*ptype.margin
        if ptype.cover_size != 0:
            cover_size=ptype.cover_size

        if album['images']:
            cover_url = None
            for image in album['images']:
                if image['width'] == 640 and image['height'] == 640:
                    cover_url = image['url']
                    break

            if cover_url:
                cover=sw.get_album_cover_from_url(cover_url)
        cover=cover.resize((cover_size, cover_size))
        cover_x = (ptype.width - cover_size) // 2
        cover_y = ptype.margin
        poster.paste(cover, (cover_x, cover_y))

    def generate_poster(self,sw:SpotifyWrapper,ptype:PosterType, album,tracks,poster_style):   
        if poster_style =="Auto":
            poster_style="Standard" # set it to standard unless we find a reason to swith to long, clean this

            album_name=album['name']
            artist_names = ", ".join([artist['name'] for artist in album['artists']])

            if len(album_name)>40 or len(artist_names)>40:
                poster_style = "Long name"

        if poster_style == "Standard":
            return self.generate_poster_standard(sw,ptype,album,tracks)
        elif poster_style == "Long name":
            return self.generate_poster_long(sw,ptype,album,tracks)


    def generate_poster_standard(self,sw:SpotifyWrapper,ptype:PosterType, album,tracks):
        poster = Image.new('RGB', (ptype.width, ptype.height), 'white')
        draw = ImageDraw.Draw(poster)
        
        ## to avoid passing too many margins around, the sections are not extracted to methods
        ## cover
        cover_size = ptype.width-2*ptype.margin
        if ptype.cover_size != 0:
            cover_size=ptype.cover_size

        if album['images']:
            cover_url = None
            for image in album['images']:
                if image['width'] == 640 and image['height'] == 640:
                    cover_url = image['url']
                    break

            if cover_url:
                cover=sw.get_album_cover_from_url(cover_url)
        cover=cover.resize((cover_size, cover_size))
        cover_x = (ptype.width - cover_size) // 2
        cover_y = ptype.margin
        poster.paste(cover, (cover_x, cover_y))

        ## title
        album_name=album['name']
        artist_names = ", ".join([artist['name'] for artist in album['artists']])
        title_y = cover_y + cover_size + ptype.section_margin 
        title_bbox = draw.textbbox((0, 0), album_name, font=self.title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = ptype.margin
        draw.text((title_x, title_y), album_name, fill='black', font=self.title_font)
        
    
        ## artist
        artist_y = title_y + 70 + 5  # title font size 
        artist_bbox = draw.textbbox((0, 0), artist_names.upper(), font=self.artist_font)
        artist_width = artist_bbox[2] - artist_bbox[0] 
        artist_x = ptype.margin
        draw.text((artist_x, artist_y), artist_names.upper(), fill='#666666', font=self.artist_font)

        ## color pallet
        num_pallet=5
        color_pallet = ColorTools.extract_color_palette(cover,num_pallet)
        if color_pallet:
            ## color_y = artist_y + 60+5 # artist font size
            color_y=(title_y+artist_y)//2 ##
            color_size = 80
            #start_x = (ptype.width - (len(color_pallet) * (color_size ))) // 2
            start_x=ptype.width-((num_pallet*color_size)+ptype.margin)
            for i, color in enumerate(color_pallet[:num_pallet]):
                x_pos = start_x + (i * (color_size ))
                draw.rectangle([x_pos, color_y, x_pos + color_size, color_y + color_size], fill=color)

        ## songs 2 alternate col
        songs_y = artist_y + 60+40 + ptype.section_margin  
        #col1_x = ptype.margin + 100
        #col2_x = (ptype.width-2*ptype.margin)//2
        col1_x = ptype.margin+2*10 
        col2_x = (ptype.width)//2
        is_even=True
        
        for track in tracks["items"]:
            track_name=f"{track['track_number']}.{track['name']}"
            track_name_len=len(track_name)
            if is_even:
                draw.text((col1_x, songs_y), track_name, fill='black', font=self.song_font)
                if track_name_len>38:
                    is_even=True
                    songs_y=songs_y+60
                else:
                    is_even=False

            elif (track_name_len>35) and is_even: 
                draw.text((col1_x, songs_y), track_name, fill='black', font=self.song_font)
                songs_y=songs_y+60
                is_even=True
            elif (track_name_len>38) and not is_even:
                songs_y=songs_y+60 # go to next line  
                draw.text((col1_x, songs_y), track_name, fill='black', font=self.song_font)
                songs_y=songs_y+60
                is_even=True
            elif not is_even:
                draw.text((col2_x, songs_y), track_name, fill='black', font=self.song_font)
                songs_y=songs_y+60
                is_even=True

        total_ms = sum(track.get('duration_ms', 0) for track in tracks["items"])
        total_seconds = total_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        total_duration= f"{minutes}m {seconds}s"

        ## bottom left scan code, calculate size to always fill
        scan_cd=sw.get_scan_code(album['id'])
        #scan_y=songs_y+ptype.section_margin
        #scan_x=ptype.width//2
        #poster.paste(scan_cd, (scan_x, scan_y))

        scan_y=songs_y+ptype.section_margin
        available_y = ptype.height-ptype.margin-scan_y
        if available_y >=90:
            # no need to shrink
            scan_y=scan_y+(available_y//2)-80
            available_x=(ptype.width//2)-ptype.margin
            ## scan_x=int((available_x-160+available_x//2)) ## right center aligned
            ## scan_x=ptype.width-ptype.margin-640 ##right aligned
            scan_x = ptype.width//2-320
            poster.paste(scan_cd, (scan_x, scan_y))

            # Release date
            info_y=scan_y+40
            info_x= (((ptype.width//2) - ptype.margin-320)//2)
            draw.text((info_x, info_y), "RELEASE DATE", fill='black', font=self.info_font)
            draw.text((info_x, info_y + 40+20), album['release_date'], fill='#666666', font=self.info_font)

            runtime_x=(ptype.width//2)+320+(((ptype.width//2) - ptype.margin-320)//2)
            draw.text((runtime_x, info_y), "RUNTIME", fill='black', font=self.info_font)
            draw.text((runtime_x, info_y + 40+10), total_duration, fill='#666666', font=self.info_font)

        #todo shrink scna code

        
        return poster
    

    def generate_poster_long(self,sw:SpotifyWrapper,ptype:PosterType, album,tracks):
        poster = Image.new('RGB', (ptype.width, ptype.height), 'white')
        draw = ImageDraw.Draw(poster)
        
        ## to avoid passing too many margins around, the sections are not extracted to methods
        ## cover
        cover_size = ptype.width-2*ptype.margin
        if ptype.cover_size != 0:
            cover_size=ptype.cover_size

        if album['images']:
            cover_url = None
            for image in album['images']:
                if image['width'] == 640 and image['height'] == 640:
                    cover_url = image['url']
                    break

            if cover_url:
                cover=sw.get_album_cover_from_url(cover_url)
        cover=cover.resize((cover_size, cover_size))
        cover_x = (ptype.width - cover_size) // 2
        cover_y = ptype.margin
        poster.paste(cover, (cover_x, cover_y))

        ## title
        album_name=album['name']
        artist_names = ", ".join([artist['name'] for artist in album['artists']])
        title_y = cover_y + cover_size + ptype.section_margin 
        title_bbox = draw.textbbox((0, 0), album_name, font=self.title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = ptype.margin
        draw.text((title_x, title_y), album_name, fill='black', font=self.title_font)

        ## artist
        artist_y = title_y + 70 + 5  # title font size 
        artist_bbox = draw.textbbox((0, 0), artist_names.upper(), font=self.artist_font)
        artist_width = artist_bbox[2] - artist_bbox[0] 
        artist_x = ptype.margin
        draw.text((artist_x, artist_y), artist_names.upper(), fill='#666666', font=self.artist_font)

        ## try code next to title
        code_rendered=False
        if len(album_name)<30 and len(artist_names)<30:
            scan_cd=sw.get_scan_code(album['id'])
            scan_y=cover_y + cover_size + ptype.section_margin 
            scan_x=ptype.width-ptype.margin-640
            poster.paste(scan_cd, (scan_x, scan_y))
            code_rendered=True

        ## long color pallet
        num_pallet=5
        color_pallet = ColorTools.extract_color_palette(cover,num_pallet)
        if color_pallet:
            color_y = artist_y + 60+4*ptype.section_margin # artist font size
            ##color_y=(title_y+artist_y)//2 ##
            color_size_y = 50 ## narrower line
            color_size_x = (ptype.width-2*ptype.margin)//num_pallet
            start_x = ptype.margin
            for i, color in enumerate(color_pallet[:num_pallet]):
                x_pos = start_x + (i * (color_size_x ))
                draw.rectangle([x_pos, color_y, x_pos + color_size_x, color_y + color_size_y], fill=color)

        ## songs 2 alternate col
        songs_y = ptype.margin+cover_size+160+8*ptype.section_margin
        #col1_x = ptype.margin + 100
        #col2_x = (ptype.width-2*ptype.margin)//2
        col1_x = ptype.margin+2*10 
        col2_x = (ptype.width)//2
        is_even=True
        
        for track in tracks["items"]:
            track_name=f"{track['track_number']}.{track['name']}"
            track_name_len=len(track_name)
            if is_even:
                draw.text((col1_x, songs_y), track_name, fill='black', font=self.song_font)
                if track_name_len>38:
                    is_even=True
                    songs_y=songs_y+60
                else:
                    is_even=False

            elif (track_name_len>35) and is_even: 
                draw.text((col1_x, songs_y), track_name, fill='black', font=self.song_font)
                songs_y=songs_y+60
                is_even=True
            elif (track_name_len>38) and not is_even:
                songs_y=songs_y+60 # go to next line  
                draw.text((col1_x, songs_y), track_name, fill='black', font=self.song_font)
                songs_y=songs_y+60
                is_even=True
            elif not is_even:
                draw.text((col2_x, songs_y), track_name, fill='black', font=self.song_font)
                songs_y=songs_y+60
                is_even=True

        total_ms = sum(track.get('duration_ms', 0) for track in tracks["items"])
        total_seconds = total_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        total_duration= f"{minutes}m {seconds}s"

        ## bottom left scan code, calculate size to always fill
        scan_cd=sw.get_scan_code(album['id'])
        #scan_y=songs_y+ptype.section_margin
        #scan_x=ptype.width//2
        #poster.paste(scan_cd, (scan_x, scan_y))

        scan_y=songs_y+ptype.section_margin
        available_y = ptype.height-2*ptype.margin-scan_y
        print(available_y)
        if available_y >=160:
            # no need to shrink
            scan_y=scan_y+(available_y//2)-80
            available_x=(ptype.width//2)-ptype.margin
            ## scan_x=int((available_x-160+available_x//2)) ## right center aligned
            ## scan_x=ptype.width-ptype.margin-640 ##right aligned
            scan_x = ptype.width//2-320
            if not code_rendered:
                poster.paste(scan_cd, (scan_x, scan_y))

            # Release date
            info_y=scan_y+40
            info_x= (((ptype.width//2) - ptype.margin-320)//2)
            draw.text((info_x, info_y), "RELEASE DATE", fill='black', font=self.info_font)
            draw.text((info_x, info_y + 40+20), album['release_date'], fill='#666666', font=self.info_font)

            runtime_x=(ptype.width//2)+320+(((ptype.width//2) - ptype.margin-320)//2)
            draw.text((runtime_x, info_y), "RUNTIME", fill='black', font=self.info_font)
            draw.text((runtime_x, info_y + 40+10), total_duration, fill='#666666', font=self.info_font)

        #todo shrink scna code

        
        return poster
    


