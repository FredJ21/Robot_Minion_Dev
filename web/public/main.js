


// Connexion au serveur WebSocket
var socket = io();

// ?couter l'?v?nement 'error' provenant du serveur
socket.on('error', function (message) {
  console.error('Erreur : ' + message);
});

// Fonction pour jouer un son
function playSound(file) {
  socket.emit('play-sound', file);
}

// Exemple d'utilisation : jouer le fichier "test.mp3"
//playSound('test.mp3');

// Fonction pour la bouche
function bouche(val) {
  socket.emit('bouche', val);
}

function bras(val) {
  socket.emit('bras', val);
}

function oeil(val_x, val_y) {
  socket.emit('oeil', {x: val_x, y: val_y});
}

function mySystem(val) {
  socket.emit('mySystem', val);
}

function sequence(val) {
  socket.emit('sequence', val);
}
// ----------------------------------------------------------------------------
// pour définir le chemin du flux vidéo (avec l'adresse IP)
//
function setVideoSource() {
  var videoElement = document.getElementById('video');
  var hostName = window.location.hostname;
  var videoUrl = 'http://' + hostName + ':8000/video_feed';
  videoElement.src = videoUrl;
}

// ----------------------------------------------------------------------------
// 	Clavier
var keysPressed = [];
//var allowedKeys = ['Alt', 'Shift', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ', 'Enter'];
var allowedKeys = ['Shift', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ', 'Enter'];

document.addEventListener('keydown', function(event) {
  var key = event.key;

  console.log("key down", key);

  if ( allowedKeys.includes(key) ) {
	event.preventDefault(); // Empêche le défilement de la page

  	if (!(keysPressed.includes(key)) ) {

  		keysPressed.push(key);
  	}
  }
});


document.addEventListener('keyup', function(event) {
  var key = event.key;
  
  // Supprimer la touche du tableau si elle est relâchée
  var index = keysPressed.indexOf(key);
  if (index > -1) {
    	keysPressed.splice(index, 1);
  }
});

// Créer un événement périodique toutes les 0,1 seconde
setInterval(function() {
  if (keysPressed.length > 0) {
    	socket.emit('keyPressed', keysPressed); // Envoyer le tableau des touches au serveur
  }
}, 100);

// ----------------------------------------------------------------------------
// Executer après le chargement du DOM 
// Gestion de la souris sur l'image

document.addEventListener('DOMContentLoaded', function() {
  
  setVideoSource();

  const imageElement = document.getElementById('video');

  const img_min_X = 0;
  const img_max_X = 512;
  const img_min_Y = 0;
  const img_max_Y = 384;

  const mapped_min_X = 800;
  const mapped_max_X = 300;
  const mapped_min_Y = 350;
  const mapped_max_Y = 650;



  let mouseDown = false;

  imageElement.addEventListener('mousedown', (event) => {
    if (event.button === 0) { // V?rifie le bouton gauche de la souris
      mouseDown = true;
      event.preventDefault(); // Emp?che la s?lection d'image
    }
  });

  imageElement.addEventListener('mouseup', () => {
    mouseDown = false;
  });
  
  imageElement.addEventListener('mouseleave', function() {
    mouseDown = false;
  });

  imageElement.addEventListener('mousemove', (event) => {
    if (mouseDown) {
	const imageRect = imageElement.getBoundingClientRect();
      	const x = event.clientX - imageRect.left;
      	const y = event.clientY - imageRect.top;

      	// Calculer les valeurs mappées vers les nouvelles plages
	var mappedX = (x - img_min_X) / (img_max_X - img_min_X) * (mapped_max_X - mapped_min_X) + mapped_min_X;
	var mappedY = (y - img_min_Y) / (img_max_Y - img_min_Y) * (mapped_max_Y - mapped_min_Y) + mapped_min_Y;
	mappedX = Math.floor(mappedX);
	mappedY = Math.floor(mappedY);
      	console.log('Position relative :', mappedX, mappedY);

	oeil(mappedX, mappedY);
    }
  });

  imageElement.addEventListener('dragstart', (event) => {
    event.preventDefault(); // Emp?che le comportement de "dragstart"
  });
});






