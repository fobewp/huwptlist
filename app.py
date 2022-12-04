# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import flask
import toolforge
import datetime
import urllib.request
import re

app = flask.Flask(__name__)

@app.route('/')
def index():
  conn = toolforge.connect('huwiki','analytics') # conn is a pymysql.connection object.
  query = ""
  with open('query.sql','r') as file:
    query = file.read().replace('\n',' ')
  rows = 0
  output  = '<head></head>\n'
  style   = 'body { font-family: sans-serif; }'
  style  += 'table { background-color: #f8f9fa; color: #202122; margin: 1em 0; border: 1px solid #a2a9b1; border-collapse: collapse; }'
  style  += 'th { background-color: #eaecf0; text-align: center;  border: 1px solid #a2a9b1; padding: 0.2em 0.4em; color: #202122; border-collapse: collapse; }'
  style  += 'td { border: 1px solid #a2a9b1; padding: 0.2em 0.4em; color: #202122; border-collapse: collapse; }'
  style  += 'a { text-decoration: none; color: #0645ad; background: none; }'
  style  += '.tddate {text-align: center;}'
  style  += '.tddays {text-align: center;}'
  style  += '.tdnum {text-align: center;}'
  script  = 'function sortTable(n) { var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0; table = document.getElementById("discussions"); switching = true; /* Set the sorting direction to ascending: */ dir = "asc"; /* Make a loop that will continue until no switching has been done: */ while (switching) { /* Start by saying: no switching is done: */ switching = false; rows = table.rows; /* Loop through all table rows (except the first, which contains table headers): */ for (i = 1; i < (rows.length - 1); i++) { /* Start by saying there should be no switching: */ shouldSwitch = false; /* Get the two elements you want to compare, one from current row and one from the next: */ x = rows[i].getElementsByTagName("TD")[n]; y = rows[i + 1].getElementsByTagName("TD")[n]; /* Check if the two rows should switch place, based on the direction, asc or desc: */ if (dir == "asc") { if (n == 2 || n == 4 || n == 5) { if (parseInt(x.innerHTML.split(" ")[0]) > parseInt(y.innerHTML.split(" ")[0])) { shouldSwitch = true; break; } } else if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) { /* If so, mark as a switch and break the loop: */ shouldSwitch = true; break; } } else if (dir == "desc") { if (n == 2 || n == 4 || n == 5) { if (parseInt(x.innerHTML.split(" ")[0]) < parseInt(y.innerHTML.split(" ")[0])) { shouldSwitch = true; break; } } else if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) { /* If so, mark as a switch and break the loop: */ shouldSwitch = true; break; } } } if (shouldSwitch) { /* If a switch has been marked, make the switch and mark that a switch has been done: */ rows[i].parentNode.insertBefore(rows[i + 1], rows[i]); switching = true; /* Each time a switch is done, increase this count by 1: */ switchcount ++; } else { /* If no switching has been done AND the direction is "asc", set the direction to "desc" and run the while loop again. */ if (switchcount == 0 && dir == "asc") { dir = "desc"; switching = true; } } } }'
  output += '<style>'+style+'</style>'
  output += '<script>'+script+'</script>'
  output += '<body>'
  with conn.cursor() as cur:
    rows = cur.execute(query) # number of affected rows
    output += '<p>Jelenleg <b>'+str(rows)+'</b> törlési megbeszélés van folyamatban. Ez a táblázat ezekről nyújt áttekintést. A törlési megbeszélés nem szavazás, a „maradjon” illetve „törlendő” álláspontokat összesítő oszlopok célja csak az, hogy iránymutatást adjanak arról, mennyire oszlanak meg a vélemények az adott megbeszélésen. A táblázat minden oldalfrissítéssel frissül (a háttérben egy adatbázis-lekérdezés fut le, ami időbe telhet). A táblázat az oszlopfejlécekre kattintva rendezhető (az „Egyéb” oszlop kivételével).</p>'
    output += '<table id="discussions">'
    output += '<tr><th onclick="sortTable(0)">Cím</th><th onclick="sortTable(1)">Megbeszélés kezdete</th><th onclick="sortTable(2)">Nyitva</th>'
    output += '<th onclick="sortTable(3)">Utolsó szerkesztés</th><th onclick="sortTable(4)">Utolsó szerkesztés</th><th onclick="sortTable(5)">Hozzászólók</th>'
    output += '<th onclick="sortTable(6)">Maradjon</th><th onclick="sortTable(7)">Törlendő</th><th>Egyéb</th></tr>'
    for i in range(rows):
      row = cur.fetchone()
      title = row[0].decode('utf-8')
      created  = datetime.datetime( int(str(row[2])[2:6]), int(str(row[2])[6:8]), int(str(row[2])[8:10]), int(str(row[2])[10:12]), int(str(row[2])[12:14]), int(str(row[2])[14:16]) )
      lastedit = datetime.datetime( int(str(row[1])[2:6]), int(str(row[1])[6:8]), int(str(row[1])[8:10]), int(str(row[1])[10:12]), int(str(row[1])[12:14]), int(str(row[1])[14:16]) )
      now = datetime.datetime.now()
      opensince = now - created  # timedelta object
      sincelast = now - lastedit # timedelta object
      actors = row[3] # number of users commenting
      votes = countvotes(title)
      tt = ''
      mm = ''
      if votes['m'] > 0:
        mm = str(votes['m']) + ' <img alt="Symbol keep vote.svg" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Symbol_keep_vote.svg/15px-Symbol_keep_vote.svg.png" decoding="async" width="15" height="15" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Symbol_keep_vote.svg/23px-Symbol_keep_vote.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Symbol_keep_vote.svg/30px-Symbol_keep_vote.svg.png 2x" data-file-width="180" data-file-height="185" />'
      if votes['t'] > 0:
        tt = str(votes['t']) + ' <img alt="Symbol delete vote.svg" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/89/Symbol_delete_vote.svg/15px-Symbol_delete_vote.svg.png" decoding="async" width="15" height="15" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/89/Symbol_delete_vote.svg/23px-Symbol_delete_vote.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/89/Symbol_delete_vote.svg/30px-Symbol_delete_vote.svg.png 2x" data-file-width="180" data-file-height="185" />'
      ee = ''
      if votes['redir'] > 0:
        ee += ('<img title="átirányítás legyen" alt="Symbol redirect vote.svg" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Symbol_redirect_vote.svg/15px-Symbol_redirect_vote.svg.png" decoding="async" width="15" height="15" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Symbol_redirect_vote.svg/23px-Symbol_redirect_vote.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Symbol_redirect_vote.svg/30px-Symbol_redirect_vote.svg.png 2x" data-file-width="180" data-file-height="185" /> ' * votes['redir'])
      if votes['rename'] > 0:
        ee += ('<img title="átnevezendő" alt="Symbol move vote.svg" src="//upload.wikimedia.org/wikipedia/commons/thumb/5/50/Symbol_move_vote.svg/15px-Symbol_move_vote.svg.png" decoding="async" width="15" height="15" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/5/50/Symbol_move_vote.svg/23px-Symbol_move_vote.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/5/50/Symbol_move_vote.svg/30px-Symbol_move_vote.svg.png 2x" data-file-width="180" data-file-height="185" /> ' * votes['rename'])
      if votes['merge'] > 0:
        ee += ('<img title="összevonandó" alt="Symbol merge vote.svg" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Symbol_merge_vote.svg/15px-Symbol_merge_vote.svg.png" decoding="async" width="15" height="15" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Symbol_merge_vote.svg/23px-Symbol_merge_vote.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Symbol_merge_vote.svg/30px-Symbol_merge_vote.svg.png 2x" data-file-width="180" data-file-height="185" /> ' * votes['merge'])
      if votes['cj'] > 0:
        ee += ('<img title="cikkjelöltté legyen" alt="Gxermo2.svg" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Gxermo2.svg/15px-Gxermo2.svg.png" decoding="async" width="15" height="16" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Gxermo2.svg/23px-Gxermo2.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Gxermo2.svg/30px-Gxermo2.svg.png 2x" data-file-width="512" data-file-height="550" /> ' * votes['cj'])
      output += '<tr>'
      output += '<td><a href=https://hu.wikipedia.org/wiki/Wikipédia:'+title+'>'+title[24:].replace("_"," ")+'</a></td>'
      output += '<td class="tddate">'+str(created.date())+'</td>'
      output += '<td class="tddays">'+str(opensince.days)+' napja</td>'
      output += '<td class="tddate">'+str(lastedit.date())+'</td>'
      output += '<td class="tddays">'+str(sincelast.days)+' napja</td>'
      output += '<td class="tdnum">'+str(actors)+' fő</td>'
      output += '<td class="tdnum">'+mm+'</td>'
      output += '<td class="tdnum">'+tt+'</td>'
      output += '<td style="text-align:center;">'+ee+'</td>'
      output += '</tr>'
    output += '</table>'
  conn.close()
  output += '<p><a href="https://github.com/fobewp/huwptlist/tree/main">Forráskód</a></p>'
  output += '</body>'
  return output

def countvotes(title):
  page = urllib.request.urlopen('https://hu.wikipedia.org/wiki/'+urllib.parse.quote('Wikipédia:'+title))
  text = page.read().decode('UTF-8')
  votes = {
    't':      len(re.findall('<b>törlendő</b>',             text)),
    'm':      len(re.findall('<b>maradjon</b>',             text)),
    'redir':  len(re.findall('<b>átirányítás',              text)),
    'rename': len(re.findall('<b>átnevezendő</b>',          text)),
    'merge':  len(re.findall('<b>összevonandó</b>',         text)),
    'cj':     len(re.findall('cikkjelöltté</a> legyen</b>', text))
  }
  return votes
