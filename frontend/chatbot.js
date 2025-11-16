 
 // Inserta el mensaje del bot y ejecuta cualquier <script> embebido
    function renderBotMessage(html) {
        const container = document.querySelector(".messages-container");
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message-box", "left");
        messageDiv.innerHTML = html;
        container.appendChild(messageDiv);

        executeEmbeddedScripts(messageDiv);

        container.scrollTop = container.scrollHeight;
    }

    // Ejecuta los scripts embebidos después de renderizar el HTML
    function executeEmbeddedScripts(element) {
        setTimeout(() => {
            const scripts = element.querySelectorAll("script");
            scripts.forEach((oldScript) => {
                const newScript = document.createElement("script");
                if (oldScript.src) {
                    newScript.src = oldScript.src;
                } else {
                    newScript.textContent = oldScript.textContent;
                }
                document.body.appendChild(newScript);
                oldScript.remove();
            });
        }, 100);
    }

    function sendMessageToBot(message) {
        const container = document.querySelector(".messages-container");

        // Mostrar el mensaje del usuario
        const userBox = document.createElement("div");
        userBox.className = "message-box right";
        userBox.innerHTML = `<p>${message}</p>`;
        container.appendChild(userBox);

        // Llamada al backend Flask
        fetch("/send_message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            // respuesta del bot
            renderBotMessage(data.response);
        })
        .catch(err => {
            console.error("Error al enviar mensaje:", err);
            renderBotMessage("⚠️ Error al comunicarse con el servidor.");
        });

        container.scrollTop = container.scrollHeight;
    }

    // Botón enviar
    document.querySelector(".button-send").addEventListener("click", function(e) {
        e.preventDefault();
        const input = document.querySelector(".message-send");
        const message = input.value.trim();
        if (!message) return;

        sendMessageToBot(message);
        input.value = "";
    });

    const inputField = document.querySelector(".message-send");
    const voiceBtn = document.getElementById('voice-command-btn');
    inputField.addEventListener("keydown", function(e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            document.querySelector(".button-send").click();
        }
    });

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isListening = false;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'es-AR';

    function resetRecognitionState() {
            isListening = false;
            voiceBtn.classList.remove('active');
            voiceBtn.textContent = '🎙️';
            if (inputField.value === '🎤 Escuchando... Di tu pregunta.') {
                inputField.value = '';
            }
        }

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        console.log('🗣️ Voz reconocida:', transcript);
        
        // Muestra el texto en el input y lo envía al backend
        inputField.value = transcript; 
        sendMessageToBot(transcript);
    };

    recognition.onerror = function(event) {
        console.error('⚠️ Error en reconocimiento de voz:', event.error);
        if (event.error === 'not-allowed') {
            alert('Permiso de micrófono denegado. Por favor, habilite el micrófono para el sitio.');
        } else if (event.error !== 'no-speech') {
             renderBotMessage('<p class="error-message">Hubo un error con el reconocimiento de voz. Intente de nuevo.</p>');
        }
    };

    recognition.onend = function() {
            console.log('🛑 Reconocimiento de voz finalizado.');
            resetRecognitionState();
        };

    voiceBtn.addEventListener('click', () => {
        if (isListening) {
            recognition.stop();
        } else {
            try {
                recognition.start();
                isListening = true;
                voiceBtn.classList.add('active');
                voiceBtn.textContent = '🔴';
                inputField.value = '🎤 Escuchando... Di tu pregunta.';
            } catch (e) {
                console.error('No se pudo iniciar el reconocimiento de voz:', e);
                resetRecognitionState();
            }
        }
    });

    } else {
        console.warn('⚠️ Web Speech API no soportada en este navegador.');
        voiceBtn.style.display = 'none';
    }

    // Detectar clics en botones de opciones del chat
    document.addEventListener("click", function(e) {
        if (e.target.classList && e.target.classList.contains("option-btn")) {
            const intent = e.target.getAttribute("data-intent") || e.target.textContent.trim();
            sendMessageToBot(intent);
        }
    });

    // Modo oscuro / claro
    const themeToggle = document.getElementById("theme-toggle");

    themeToggle.addEventListener("change", () => {
        document.body.classList.toggle("dark-mode", !themeToggle.checked);
        localStorage.setItem("darkMode", themeToggle.checked ? "disabled" : "enabled");
    });

    // Cargar modo guardado
    const darkMode = localStorage.getItem("darkMode");
    if (darkMode === "enabled" || darkMode === null) {
        document.body.classList.add("dark-mode");
        themeToggle.checked = false;
    } else {
        document.body.classList.remove("dark-mode");
        themeToggle.checked = true;
    }