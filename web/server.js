const express = require('express');
const http = require('http');
const { exec } = require('child_process');

const app = express();
const server = http.createServer(app);
const io = require('socket.io')(server);

const { createProxyMiddleware } = require('http-proxy-middleware');


const soundRep = "/home/pi/FRED/Raspberry/0_SON/MINION"

// UDP Sender
const UDP = require('dgram');
const UDP_client = UDP.createSocket('udp4');
const UDP_port = 21000;
const UDP_hostname = 'localhost';
//const UDP_hostname = '10.1.23.1';


// ----------------------------------------------------------------------------
//			UDP Sender
// ----------------------------------------------------------------------------
UDP_client.on('message', (message, info) => {
  // get the information about server address, port, and size of packet received.
  console.log('[UDP rx] Address: ', info.address, 'Port: ', info.port, 'Size: ', info.size)

  //read message from server
  console.log('[UDP rx] Message from server', message.toString())
})

function UDP_send(data) {

	UDP_packet = Buffer.from(data)

	UDP_client.send(UDP_packet, UDP_port, UDP_hostname, (err) => {
		if (err) {
    		console.error('[UDP tx] Failed to send packet !!')
  		} else {
    		console.log('[UDP tx] Packet send :' + data)
  	}
})
}


// ----------------------------------------------------------------------------
// 			Envoi du fichier index.html au client
// ----------------------------------------------------------------------------
app.get('/', (req, res) => {
	res.sendFile(__dirname + '/public/index.html');
});

// Configuration du serveur Express
app.use(express.static(__dirname + '/public'));


// ----------------------------------------------------------------------------
//			Reverse Proxy 
// ----------------------------------------------------------------------------
const videoProxy = createProxyMiddleware('/video_feed', {
  target: 'http://localhost:8000',
  ws: true
});

app.use(videoProxy);


// ----------------------------------------------------------------------------
// 			Gestion des connexions WebSocket
// ----------------------------------------------------------------------------
io.on('connection', (socket) => {

	console.log('[socket] Un client WebSocket est connecté.');

  	//-------------------------------------------------------------------------
  	socket.on('play-sound', (file) => {

    	file = soundRep + "/" + file;
    	console.log("[socket rx] play : "+ file);
	  
    	//  si le nom du fichier est fourni
    	if (!file) {
      		socket.emit('error', 'Nom du fichier manquant.');
      		return;
    	}

    	// Utiliser la commande systéme pour jouer le fichier MP3
    	const command = `omxplayer ${file}`;
    	exec(command, (error, stdout, stderr) => {
      	if (error) {
        	console.error(`Erreur lors de la lecture du fichier MP3: ${error.message}`);
        	socket.emit('error', 'Erreur lors de la lecture du fichier MP3.');
        	return;
      	}
      	if (stderr) {
        	console.error(`Erreur lors de la lecture du fichier MP3: ${stderr}`);
        	socket.emit('error', 'Erreur lors de la lecture du fichier MP3.');
        	return;
      	}
      	console.log('Lecture du fichier MP3 terminée.');
    	});
  	});

	//-------------------------------------------------------------------------
  	socket.on('sequence', (val) => {
    	
		console.log("[socket rx] sequence : "+ val);

		const command = `/home/pi/FRED/Raspberry/MINION/Play_sequence.py ${val}`;
	    	exec(command, (error, stdout, stderr) => {
	      	if (error) {
        		console.error(`Erreur : ${error.message}`);
	        	return;
      		}
      		if (stderr) {
        		console.error(`Erreur2 : ${stderr}`);
        		return;
	      	}
    	});
  	});

	//-------------------------------------------------------------------------
  	socket.on('oeil', ({x, y}) => {

	    	console.log("[socket rx] oeil : "+ x +" - "+ y);

		UDP_send('{ "Oeil_X":"' + x +'", "Oeil_Y":"' + y + '" }');
  	});



  	//-------------------------------------------------------------------------
  	socket.on('bouche', (val) => {
    	console.log("[socket rx] bouche : "+ val);

		if (val == 'sourire') {
			UDP_send('{ "Bouche_D":"0", "Bouche_G":"0" }');
		}
		else if (val == 'neutre') {
			UDP_send('{ "Bouche_D":"home", "Bouche_G":"home" }');
		}
		else if (val == 'triste') {
			UDP_send('{ "Bouche_D":"1000", "Bouche_G":"1000" }');
		}
		else if (val == 'fou1') {
			UDP_send('{ "Bouche_D":"1000", "Bouche_G":"0" }');
		}
		else if (val == 'fou2') {
			UDP_send('{ "Bouche_D":"0", "Bouche_G":"1000" }');
		}

  	});

  	//-------------------------------------------------------------------------
  	socket.on('bras', (val) => {
    	console.log("[socket rx] bras : "+ val);

		if (val == 'bas') {
			UDP_send('{ "Bras_D":"200", "Bras_G":"200" }');
		}
		else if (val == 'haut') {
			UDP_send('{ "Bras_D":"800", "Bras_G":"800" }');
		}
		else if (val == 'hb1') {
			UDP_send('{ "Bras_D":"800", "Bras_G":"200" }');
		}
		else if (val == 'hb2') {
			UDP_send('{ "Bras_D":"200", "Bras_G":"800" }');
		}
		else if (val == 'horizon') {
			UDP_send('{ "Bras_D":"500", "Bras_G":"500" }');
		}
		else if (val == 'horizon1') {
			UDP_send('{ "Bras_D":"450", "Bras_G":"550" }');
		}
		else if (val == 'horizon2') {
			UDP_send('{ "Bras_D":"550", "Bras_G":"450" }');
		}

  	});

  	//-------------------------------------------------------------------------
  	socket.on('mySystem', (val) => {
    	console.log("[socket rx] mySystem : "+ val);

		if (val == 'kill_omxplayer') {
			const command = `killall omxplayer omxplayer.bin`;
		    	exec(command); 
			const command2 = "kill `ps -edf | grep Play_sequence.py | awk '{ print $2 } '`"
		    	exec(command2); 
		}
		else if (val == 'disa_opencv') {
			const command = `rm /tmp/enable_minion_opencv`;
		    	exec(command); 
		}
		else if (val == 'ena_opencv') {
			const command = `touch /tmp/enable_minion_opencv`;
		    	exec(command); 
		}
  	});




  	//-------------------------------------------------------------------------
	socket.on('keyPressed', (keys) => {
    		console.log('Touche tapée :', keys);
		
		chaine = JSON.stringify(keys);

		UDP_send('{ "KEY":'+ chaine +' }');
  	});


});

// Démarrer le serveur
const port = 3000;
server.listen(port, () => {
  console.log(`Le serveur est à l'écoute sur le port ${port}`);
});

