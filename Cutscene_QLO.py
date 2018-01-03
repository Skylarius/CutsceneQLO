#CUTSCENE - QUANTUM LEAP OPERATION
#Videogioco multigiocatore in LAN. Ogni giocatore che esegue il gioco sul proprio pc può scegliere all'inizio la direzione in cui sparare,
#quindi sullo schermo di ogni pc comparirà un personaggio rivolto verso quella direzione posto in una schermata nera.
#Questo può quindi sparare e i proiettili passeranno da uno schermo all'altro, atti a colpire il nemico, per togliergli energia.
#Il gioco termina quando uno dei due player resta senza energia

#Funzionamento Effettivo:
#Ciascun giocatore sceglie la direzione verso cui sparare digitandola sulla schermata di avvio
#Il gioco usa le socket: Si dovrà stabilire chi è il client e chi è il server. Questa scelta è lasciata gestire agli utenti
#Il gioco inizia. Entrambi i giocatori muovono il personaggio principale con il mouse e possono: 
# 1) Sparare con il tasto sinistro del mouse o Spacebar un PROIETTILE che si muoverà lungo l'asse orizzontale e che appena toccherà il bordo di una finestra,
#scomparirà da questa per riapparire sull'altra finestra su uno dei due bordi, in base a come il giocatore ha scelto la direzione di sparo
# 2) Sparare con il tasto destro del Mouse o RCTRL una BOMBA che comparirà sulla testa del giocatore avversario provocandogli ingenti danni in caso di successo, 
#ma solo se la percentuale di caricamento della bomba è al 100%. Dopo ogni bomba la percentuale viene settata a 0%
# 3) Sparare con il tasto centrale del mouse o con LCTRL dei MULTIPLI PROIETTILI contemporaneamente, più difficili da evitare per l'avversario. Questo può avvenire
# solo se la percentuale di caricamento della bomba è superiore a 50%, ogni volta che si usa questa funzione si sottrae il 20% alla percentuale
# La partita termina quando uno dei due giocatori non esaurisce la sua energia. Viene mostrato il punteggio partita, il gioco va in pausa e poi ricomincia la partita

#E' necessaria la libreria pygame.

#---------------------------------------#

import pygame, sys, socket, pickle, threading
from time import sleep
from os import startfile
from pygame.locals import *

#inizializzazione e modifiche della finestra
pygame.init()
pygame.display.set_caption("CUTSCENE QLO - Quantum Leap Operation")
pygame.display.set_icon(pygame.image.load("gomezico.ico"))
pygame.mouse.set_visible(False)



#costanti
black = 0,0,0
resolution=1280,720
border=0
damage=7
MAXBULLETONSCREEN=15
MAXTIMEBOMB=1000 #centomila
STARTSPEEDBOMB=2
FPS_DES=72
FRACTION_DIVISION_COUNTER=20
speedp2=20

#VARIABILI GLOBALI
stato="null"
speed=35
speedbomb=STARTSPEEDBOMB
isBomb=False
pos_bomb=[0,2*resolution[1]] #inizialmente metto la posizione della bomba molto lontano dalle possibilità di raggiungimento del giocatore
life=100
percentBomb=80
counterBomb=1200
punteggio=[0,0]
clock=pygame.time.Clock()
fullscreen=True
p2pos=[resolution[0]//2, resolution[1]//2]
isPlayer2=False

#PARTE UNO: IMPOSTAZIONI INIZIALI DI GIOCO
#In base alla scelta della direzione si caricano le immagini appropriate: player è il giocatore, shoot il proiettile, shoot_enemy il proiettile avversario.
#Inoltre si settano le variabili, quali la velocità (positiva verso destra, negativa verso sinistra) e il bordo di passaggio del proiettile
#Nota: lo sfondo è stato rimosso perchè incideva troppo sulle prestazioni
while True:
    direction=input("Inserisci la direzione verso cui spari ('destra' oppure 'sinistra')\n->")
    if direction == 'sinistra':
        player=pygame.image.load("gomezleft.png")
        p2=pygame.image.load("pixelParrotleft.png")
        shoot=pygame.image.load("shootleft.png")
        shoot_enemy=pygame.image.load("shootright.png")
        bomb=pygame.image.load("bombleft.png")
        speed=-speed
        border=0
        #background=pygame.image.load("backgroundleft.jpg")
        #background=pygame.transform.scale(background,(1280,720))
        Audio=[pygame.mixer.Sound("damage1.wav"),pygame.mixer.Sound("laser1.wav"),pygame.mixer.Sound("explosion1.wav")]
        break
    elif direction =='destra':
        player=pygame.image.load("gomezright.png")
        p2=pygame.image.load("pixelParrotright.png")
        shoot=pygame.image.load("shootright.png")
        shoot_enemy=pygame.image.load("shootleft.png")
        bomb=pygame.image.load("bombright.png")
        border=resolution[0]
        #background=pygame.image.load("backgroundright.jpg")
        #background=pygame.transform.scale(background,(1280,720))
        Audio=[pygame.mixer.Sound("damage2.wav"),pygame.mixer.Sound("laser2.wav"),pygame.mixer.Sound("explosion2.wav")]
        break
    else: print("Errore: reinserire comando\n")

#CREA PARTITA / UNISCITI
#Uno dei due giocatori deve essere il server (crea la partita col comando 'new'), l'altro il client (si unisce alla partita creata dal server con 'join')
while True:
    command=input("Crei una partita o entri in una creata? ('new' oppure 'join')\n->")
    #SERVER
    if command=='new':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nameserver=socket.gethostname()
        server_address = (socket.gethostbyname(nameserver), 10000)
        print ('Server: %s, porta: %s\n' % server_address)
        sock.bind(server_address)
        sock.listen(1)
        try:
            print ('Attendo avversario')
            sock.settimeout(40)
            connection, client_address = sock.accept()
            print("Connessione stabilita con %s\n. VIA TRA 5 SECONDI..." % socket.gethostbyaddr(client_address[0])[0])
            sleep(5)
            break
        except socket.timeout: print("Timeout scaduto: ricominciare\n")
    #CLIENT
    elif command=='join':
        ip=input("Inserisci l'indirizzo IP dell'avversario\n->")
        if ip=='local': ip=socket.gethostname()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip, 10000)
        try:
            print ('Tento connessione con %s sulla porta %s' % server_address)
            sock.connect(server_address)
            print ('Connessione stabilita con %s\n. VIA TRA 5 SECONDI...' % socket.gethostbyaddr(server_address[0])[0])
            sleep(5)
            break;
        except socket.timeout: print("Timeout scaduto: ricominciare\n")
        except ConnectionRefusedError: print("Impossibile stabilire la connessione: ricominciare\n")

#INIZIALIZZO LA RISOLUZIONE E IL FONT GENERALE
pygame.font.init()
myfont = pygame.font.Font("8bit.ttf", 32)
screen=pygame.display.set_mode(resolution, pygame.FULLSCREEN)


#I proiettili passano attraverso tre stadi caratterizzati da tre liste di coppie di interi:
#bullets contiene le posizioni dei proiettili sparati dal giocatore che stanno ancora sulla sua schermata
#bullets_incoming contiene le pos dei proiettili sparati dall'avversario che stanno sulla propria schermata
#bullets_send è il vettore che viene riempito con le pos dei proiettili che toccano il bordo (destro o sinistro) dello schermo. Viene usato dalle socket.

bullets=[] 
bullets_incoming=[] 
bullets_send=[]

#STRUTTURA ARMI:
# 1) Proiettili: definiti dalla loro immagine e da coppie di numeri che corrispondono alla posizione (esempio [1,2]
# 2) Bombe: definite dalla loro immagine e da una lista di due elementi dove il primo è una coppia di numeri che corrisponde alla posizione e il secondo il tag "bomba" (esempio [[1,2],"bomb"]

#LE SOCKET:
#Nota: Per rendere le socket bloccanti ma non bloccare il gioco ho deciso di creare due thread che gestissero le socket. Qui di seguito le loro funzioni caratteristiche

#SOCKET_SEND: ha tre funzionalità:
# 1) Guarda nel vettore bullets_send se ci sono elementi, li prende, li manda alla socket e li cancella da bullets_send.
# 2) Controlla se il giocatore sull'host che la esegue è morto: in tal caso manda alla socket una stringa "morto"
# 3) Controlla se il giocatore sull'host che la esegue ha sganciato una bomba: in tal caso manda una stringa "BOMB"

def socket_send(threadname):
    global bullets_send
    global life
    global command
    global stato
    global isBomb
    while True:
        for info in bullets_send:
            message=pickle.dumps(info)
            if command=="new": #SONO IL SERVER
                connection.send(message)
            elif command=="join": #SONO IL CLIENT
                print(sock.send(message))
            print("Send %s" % info)
            bullets_send.remove(info)
        if life<=0:
            stato="lose"
            if command=="new": #SONO IL SERVER
                for i in range(0,1): connection.send(pickle.dumps("morto"))
                sleep(5)
                
            elif command=="join": #SONO IL CLIENT
                for i in range(0,1): sock.send(pickle.dumps("morto"))
                sleep(5)   
        if isBomb:
            message=pickle.dumps("BOMB")
            if command=="new": #SONO IL SERVER
                connection.send(message)
            elif command=="join": #SONO IL CLIENT
                sock.send(message)
            print("BOMB")
            isBomb=False
            
#SOCKET_RECIVE: Ascolta la socket e distingue i tre casi di SOCKET_SEND nell'ordine seguente:
# 1) Se il dato ricevuto è una stringa con su scritto "morto" vuol dire che il giocatore avversario ha perso, quindi cambia la variabile globale 'stato' in "win"
# 2) Altrimenti se il dato ricevuto è la stringa "BOMB" setta la variabile globale pos_bomb con coordinate (giocatore_x, 0) per piazzare una bomba sulla testa del giocatore
# 3) Se il dato non è nè 1 nè 2 allora sarà la coordinata y del proiettile avversario. crea la coppia [bordo_opposto, coordinata_y_ricevuta] e la mette nella lista bullets_incoming
def socket_recive(threadname):
    global bullets_incoming
    global stato
    global command
    global pos_bomb
    while True:
        if command=="new": #SONO IL SERVER
            try:
                data=connection.recv(4096)
            except ConnectionResetError:
                stato="Connessione Client Persa"
                sleep(6)
  
        elif command=="join": #SONO IL CLIENT
            try: 
                data=sock.recv(4096)
            except ConnectionResetError:
                stato="Connessione Server Persa"
                sleep(6)

        data=pickle.loads(data)
        if str(data)=="morto":
            print(str(data))
            stato="win"
            if command=="new": #SONO IL SERVER
                sleep(6)
                #connection.close()
            elif command=="join": #SONO IL CLIENT
                sleep(6)
                #sock.close() 
            
        elif str(data)=="BOMB":
            pos_bomb=[pygame.mouse.get_pos()[0],-90]
            print("posbomb %s" % pos_bomb)
        else:
            bullets_incoming.append([border,data])
        print("Recived %s" % data)

#DANNO PROIETTILI: calcolato in base alla precisione con cui si viene colpiti.    
def calc_damage(x):
    global damage
    if x<0: x=-x
    x=x/40
    val=damage*x
    return int(val)

    
        

#AVVIO THREAD
threading._start_new_thread(socket_send,("send",))
threading._start_new_thread(socket_recive,("recive",))

#MOSTRA TITOLO
title=pygame.image.load("title.png")
screen.fill(black)
screen.blit(title,[307,172])
pygame.display.update()
sleep(3)


#INIZIO LOOP DI GIOCO:
while True:
    for event in pygame.event.get():
        #USCITA:
        #Per uscire dal gioco si può chiudere la finestra con il mouse oppure premere ESC
        if event.type == pygame.QUIT or (event.type == KEYDOWN and pygame.key.get_pressed()[K_ESCAPE]):
            pygame.quit() 
            sys.exit()
        #FULLSCREEN
        if event.type == pygame.QUIT or (event.type == KEYDOWN and pygame.key.get_pressed()[K_f]):
            if fullscreen: 
                screen=pygame.display.set_mode(resolution)
                fullscreen=False
            else: 
                screen=pygame.display.set_mode(resolution, pygame.FULLSCREEN)
                fullscreen=True
        #GESTIONE EVENTI DEI TASTI
        #SPARO PROIETTILI: Tasto sinistro mouse oppure barra spaziatrice.
        #Si setta la posizione iniziale dei proiettili rispetto al player che li ha sparati e si mette il dato nella lista bullets
        if ((event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]) or (event.type == KEYDOWN and pygame.key.get_pressed()[K_SPACE])) and len(bullets) < MAXBULLETONSCREEN:
            Audio[0].play()
            shootpos=[0,0]
            shootpos[0]=pygame.mouse.get_pos()[0] + player.get_width()//4
            shootpos[1]=pygame.mouse.get_pos()[1] + player.get_height()//4
            bullets.append(shootpos)
        #SPARO BOMBE: tasto destro del mouse o RCTRL AND percentuale caicamento bomba 100%
        #Con un booleano si comunica al thread socket_send che ho sganciato una bomba, quindi si resetta la percentuale di caricamento bomba
        if ((event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]) or (event.type == KEYDOWN and pygame.key.get_pressed()[K_RCTRL])) and percentBomb==100:   
            Audio[0].play()
            counterBomb=0 #Questo è un numero che funge da timer logico per regolare la velocità di caricamento percentuale bomba
            percentBomb=0
            isBomb=True
        #SPARO MULTIPLO: tasto centrale del mouse oppure LCTRL AND percentuale caricamento bomba > 50%
        #Itero 15 volte automaticamente il meccanismo di SPARO PROIETTILI, per creare una pila di proiettili sparati. Sottraggo un po' di percentuale caricamento bomba
        #Lo sfasamento rispetto all'asse x serve a evitare che arrivino più proiettili contemporaneamente generando perdite di dati. 
        if ((event.type == KEYDOWN and pygame.key.get_pressed()[K_LCTRL]) or (event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1])) and percentBomb>50:
            Audio[0].play()
            for i in range(0,15):
                shootpos=[0,0]
                shootpos[0]=pygame.mouse.get_pos()[0] + player.get_width()/4 -i*100
                shootpos[1]=(resolution[0]*i)//10 + pygame.mouse.get_pos()[1]//10
                print(shootpos)
                bullets.append(shootpos)
            counterBomb-=40*40
            percentBomb-=40
			
		#GESTIONE PAPPAGALLO
        #Dalla versione 1.2 E' possibile inserire un pratico pappagallo per giocare in COOP
        if (event.type == KEYDOWN and pygame.key.get_pressed()[K_m]): isPlayer2=True

        if (event.type == KEYDOWN and pygame.key.get_pressed()[K_LSHIFT]) and len(bullets) < MAXBULLETONSCREEN and isPlayer2:
            Audio[0].play()
            shootpos=[0,0]
            shootpos[0]=p2pos[0] + p2.get_width()/4
            shootpos[1]=p2pos[1] + p2.get_height()/4
            bullets.append(shootpos)

        if isPlayer2:
            keypress=pygame.key.get_pressed()
            if keypress[K_w]: p2pos[1]-=speedp2
            if keypress[K_s]: p2pos[1]+=speedp2
            if keypress[K_a]: p2pos[0]-=speedp2
            if keypress[K_d]: p2pos[0]+=speedp2
            
    #CALCOLO POSIZIONI DELLA GRAFICA:

    #screen.blit(background,(0,0))
    screen.fill(black)
    black=0,0,0
    screen.blit(player,pygame.mouse.get_pos())
    if isPlayer2: screen.blit(p2,p2pos)
    label = myfont.render("ENERGY "+ str(life), 1, (255,255,255))
    screen.blit(label, (0,0))
    label2 = myfont.render("BOMB "+ str(percentBomb) +"%", 1, (255,0,0))
    screen.blit(label2, (0,22)) 
      
    #PROIETTILI USCENTI:
    #Tutti i proiettili sparati avanzano di (speed) pixel IN DIREZIONE OPPOSTA al giocatore. Se escono dallo schermo scompaiono (vengono rimossi dalla lista bullet)
    #Appena scompaiono vengono inserite le coordinate verticali di ogni proiettile in bullets_send, lista usata dalla socket_send
    for bullet in bullets:
        screen.blit(shoot,bullet)
        bullet[0]+=speed #muove il proiettile verso l'avversario a ogni loop
        
        #SCOMPARSA DALLO SCHERMO
        if (bullet[0]>resolution[0]+10 or bullet[0]<-10):
            bullets_send.append(bullet[1])
            bullets.remove(bullet)

    #PROIETTILI ENTRANTI
    #I proiettili avversari avanzano di (speed) pixel VERSO il giocatore. Se scompaiono dallo schermo vengono rimossi dalla lista bullets_incoming (scompaiono per sempre)
    for bullet in bullets_incoming:
        screen.blit(shoot_enemy,bullet)
        bullet[0]+=-speed #muove il proiettile verso il player a ogni loop

        #SCOMPARSA DALLO SCHERMO
        if (bullet[0]>resolution[0]+10 or bullet[0]<-10):
            bullets_incoming.remove(bullet)
        
        #COLPO SUBITO: 
        #Se si viene colpiti si perde energia, ciò è segnalato dal lampeggiamento della schermata di gioco (bianco per i proiettili, rosso per le bombe)
        if (-40 <= pygame.mouse.get_pos()[0]-bullet[0] <= 40 and -40 <= pygame.mouse.get_pos()[1]-bullet[1] <= 40):
            
            life-=calc_damage(min(pygame.mouse.get_pos()[0]-bullet[0],pygame.mouse.get_pos()[1]-bullet[1]))
            black=255,255,255
            print(str(life))
            Audio[1].play()
            bullets_incoming.remove(bullet)
    
    #AVANZAMENTO CARICAMENTO BOMBA:
    #Qui la variabile percentuale di caricamento bomba e il suo timer logico (counterBomb)
    if isBomb==False and percentBomb<100:
        percentBomb=counterBomb//FRACTION_DIVISION_COUNTER
        counterBomb+=1
        

    #DISCESA BOMBA
    #Mentre i proiettli si muovono di moto rettilineo uniforme orizzontale, la bomba si muove di moto accelerato verticale verso il basso
    if pos_bomb[1]<=resolution[1]+5:
        pos_bomb[1]+=int(speedbomb)
        speedbomb+=0.5
        screen.blit(bomb,pos_bomb)
    
    #GIOCATORE COLPITO DALLA BOMBA: sottraggo 20 punti di energia e lampeggia uno sfondo rosso    
    if (-60 <= pygame.mouse.get_pos()[0]-pos_bomb[0] <= 60 and -60 <= pygame.mouse.get_pos()[1]-pos_bomb[1] <= 60):
        pos_bomb[1]=resolution[1]+1000
        speedbomb=STARTSPEEDBOMB
        screen.blit(bomb,pos_bomb)
        black=255,0,0
        life-=20

    #VITTORIA/SCONFITTA E RESTART!
    #Lo stato è inizialmente messo a "null". Se viene messo a "win" compare la scritta HAI VINTO, se viene messo a "lose" compare HAI PERSO.
    #Se nessuna delle due cose è avvenuta vuol dire che si è verificato un errore fatale. Si mostra a schermo il tipo di errore e si aspetta la terminazione manuale
    #Ogni giocatore tiene conto del punteggio delle partite. Se vince incrementa il suo, se perde incrementa quello dell'avversario (vettore punteggio)
    if(stato!="null"):
        Audio[2].play()
        myfont3=pygame.font.Font("8bit.ttf", 80)
        if stato=="lose": 
            label2 = myfont3.render("HAI PERSO!!!", 1, (255,0,0))
            punteggio[1]+=1
        elif stato=="win": 
            label2 = myfont3.render("HAI VINTO!!!", 1, (0,255,0))
            punteggio[0]+=1
        else: 
            label2=myfont3.render(stato, 1, (255,255,255))
            screen.blit(label2, (100,resolution[1]/2+100))
            pygame.display.update()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == KEYDOWN and pygame.key.get_pressed()[K_ESCAPE]):
                        pygame.quit() 
                        sys.exit()
        screen.blit(label2, (resolution[0]/2-200,resolution[1]/2+100))

        #SCRITTURA CREDITI:
        myfont4=pygame.font.Font("8bit.ttf", 15)
        credit="Sviluppato da Ilario Gabriele Gerloni in Python con libreria Pygame - Catania, Giugno 2016"
        label_credit=myfont4.render(credit, 1, (255,255,255))
        screen.blit(label_credit, (300,resolution[1]-20))
        
        #RESET PARTITA:
        #Dopo aver mostrato i rispettivi punteggi si resetta l'energia, la percentuale caricamento bomba SE si ha vinto, 
        #si svuotano i vettori bullets, bullets_send, bullets_incoming si setta lo stato a null, si aspettano 6 secondi e inizia una nuova partita sulla stessa connessione
        myfont2=pygame.font.Font("8bit.ttf", 30)
        restart_text="Tu: "+str(punteggio[0])+" - Lui: "+str(punteggio[1])+" - Restart tra 6 secondi"
        label_punteggio=myfont2.render(restart_text, 1, (255,255,255))
        screen.blit(label_punteggio, (resolution[0]/2-200,resolution[1]/2+200))
        label_info1=myfont2.render("Premi ESC per uscire", 1, (255,255,0))
        screen.blit(label_info1, (resolution[0]/2-200,resolution[1]/2+240))
        label_info2=myfont2.render("Premi F per modalità fullscreen/windowed", 1, (255,255,00))
        screen.blit(label_info2, (resolution[0]/2-200,resolution[1]/2+280))
        if stato=="win":
            counterBomb=0
            percentBomb=0 
        stato="null"
        life=100
        bullets=[] 
        bullets_incoming=[] 
        bullets_send=[]
        
        pygame.display.update()
        sleep(6)
        

        
    #DISPLAY.UPDATE e CLOCK.TICK
    #Queste due funzioni sono fondamentali: la prima serve ad fare il refresh dello schermo, la seconda setta i massimi fotogrammi per secondo
    pygame.display.update()
    clock.tick(FPS_DES)
    
#QUESTA ZONA NON VIENE MAI RAGGIUNTA:
#Tenuta comunque come debug
pygame.display.update()
input("END\n")
sleep(2)
pygame.display.quit()
sys.exit()