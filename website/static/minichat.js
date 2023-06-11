var position = getPosition('bottom-right');
var open = false;
//initialise();
//createStyles();

function getPosition(position) {
    const [vertical, horizontal] = position.split('-');
    return {
        [vertical]: '30px',
        [horizontal]: '30px',
    };
}

function initialise(orgId,bgColor, welcomeText) {
    createStyles();
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.classList.add('chat-wrapper')
    Object.keys(position)
        .forEach(key => container.style[key] = position[key]);
    document.body.appendChild(container);

    const buttonContainer = document.createElement('div');
    buttonContainer.classList.add('button-container')
    buttonContainer.style.backgroundColor = bgColor;

    const contextDiv = document.createElement('div');
    contextDiv.classList.add('context')

    const contextConDiv = document.createElement('div');
    contextConDiv.classList.add('conDiv');

    let p = document.createElement("p");
    p.textContent = welcomeText;

    const contextConImg = document.createElement('img');
    contextConImg.classList.add('contextConImg');
    contextConImg.src = 'http://127.0.0.1:5000/static/mplay.png';

    const contextConClose = document.createElement('img');
    contextConClose.classList.add('contextConClose');
    contextConClose.src = 'http://127.0.0.1:5000/static/tclose.png';

    contextConDiv.appendChild(contextConImg);
    contextConDiv.appendChild(contextConClose);
    contextConDiv.appendChild(p);
    contextDiv.appendChild(contextConDiv);

    const chatIcon = document.createElement('img');
    chatIcon.src = 'http://127.0.0.1:5000/static/trologo.svg';
    chatIcon.classList.add('icon');
    this.chatIcon = chatIcon;

    const closeIcon = document.createElement('img');
    closeIcon.src = 'http://127.0.0.1:5000/static/uploads/cross.svg';
    closeIcon.classList.add('icon', 'hidden');
    this.closeIcon = closeIcon;

    buttonContainer.appendChild(this.chatIcon);
    buttonContainer.appendChild(this.closeIcon);
    buttonContainer.appendChild(contextDiv);

    const messageContainer = document.createElement('div');
    messageContainer.classList.add('hidden', 'message-container');
    messageContainer.classList.add('mchat');

    chatIcon.addEventListener('click', function(){
        chatIcon.classList.add('hidden');
        closeIcon.classList.remove('hidden');
        messageContainer.classList.remove('hidden');
        contextDiv.classList.add('hideContext');
        // open = !open;
        // if (open) {
        //     chatIcon.classList.add('hidden');
        //     closeIcon.classList.remove('hidden');
        //     messageContainer.classList.remove('hidden');
        //     contextDiv.classList.add('hideConext');
        // } else {
        //     //createMessageContainerContent(messageContainer);
        //     chatIcon.classList.remove('hidden');
        //     closeIcon.classList.add('hidden');
        //     messageContainer.classList.add('hidden');
        // }
    });

    closeIcon.addEventListener('click', function(){
        chatIcon.classList.remove('hidden');
        closeIcon.classList.add('hidden');
        messageContainer.classList.add('hidden');
        contextDiv.classList.remove('hideContext');
    });

    contextConClose.addEventListener('click', function(){
        contextDiv.classList.add('hideContext');
    });

    this.createMessageIframe(messageContainer, orgId);
    //this.createMessageContainerContent(messageContainer);

    container.appendChild(messageContainer);
    container.appendChild(buttonContainer);
}

function createMessageIframe(messageContainer, orgId) {
    const iframe = document.createElement('iframe');
    iframe.src = 'http://127.0.0.1:5000/minichat/' + orgId
    messageContainer.appendChild(iframe);

}

function createMessageContainerContent(messageContainer) {

    messageContainer.innerHTML = '';
    const title = document.createElement('h2');
    title.textContent = `We're not here, drop us an email...`;

    const form = document.createElement('form');
    form.classList.add('content');
    const email = document.createElement('input');
    email.required = true;
    email.id = 'email';
    email.type = 'email';
    email.placeholder = 'Enter your email address';

    const message = document.createElement('textarea');
    message.required = true;
    message.id = 'message';
    message.placeholder = 'Your message';

    const btn = document.createElement('button');
    btn.textContent = 'Submit';
    form.appendChild(email);
    form.appendChild(message);
    form.appendChild(btn);

    messageContainer.appendChild(title);
    messageContainer.appendChild(form);


}

function createStyles() {
    const styleTag = document.createElement('style');
    styleTag.innerHTML = `
        .chat-wrapper{
            z-index: 2147483647;
        }
        .mchat{
            position: absolute;
            bottom: 0;
            right: 0;
            height: 600px;
            width: 400px;
        }
        .mchat iframe{
            height: 100%;
            width: 100%;
            border: none;
        }
        .icon {
            cursor: pointer;
            width: 60%;
            position: absolute;
            top: 12px;
            left: 12px;
            transition: transform .3s ease;
        }
        .hideContext {
            display: none;
        }
        .hidden {
            transform: scale(0);
        }
        .button-container {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            position: relative;
        }
        .button-container .context {
            position: absolute;
            top: -50px;
            background-color: transparent;
            height: 80px;
            width: 250px;
            left:-270px;
            color: white;
        }
        .button-container .context .conDiv {
            position: relative;
            background-color: #ffffff;
            color: #000000;
            width: 235px;
            border-radius: 10px;
            height: 100%;
            padding: 10px;
        }
        .button-container .context .conDiv .contextConImg {
            position: absolute;
            bottom: -5px;
            right:-23px;
            width: 40px;
            height: 40px;
        }
        .button-container .context .conDiv .contextConClose {
            position: absolute;
            top: -18px;
            right:-18px;
            width: 30px;
            height: 30px;
            cursor: pointer;
        }
        .message-container {
            box-shadow: 0 0 18px 8px rgba(0, 0, 0, 0.1), 0 0 32px 32px rgba(0, 0, 0, 0.08);
            width: 400px;
            right: -25px;
            bottom: 75px;
            max-height: 600px;
            position: absolute;
            transition: max-height .2s ease;
            font-family: Helvetica, Arial ,sans-serif;
            z-index: 10000;
        }
        @media screen and (max-width: 768px) {
            .message-container {
                right: -40px;
            }
          }
        .message-container.hidden {
            max-height: 0px;
        }
        .message-container h2 {
            margin: 0;
            padding: 20px 20px;
            color: #fff;
            background-color: #007bff;
        }
        .message-container .content {
            margin: 20px 10px ;
            border: 1px solid #dbdbdb;
            padding: 10px;
            display: flex;
            background-color: #fff;
            flex-direction: column;
        }
        .message-container form * {
            margin: 5px 0;
        }
        .message-container form input {
            padding: 10px;
        }
        .message-container form textarea {
            height: 100px;
            padding: 10px;
        }
        .message-container form textarea::placeholder {
            font-family: Helvetica, Arial ,sans-serif;
        }
        .message-container form button {
            cursor: pointer;
            background-color: #007bff;
            color: #fff;
            border: 0;
            border-radius: 4px;
            padding: 10px;
        }
        .message-container form button:hover {
            background-color: #16632f;
        }
    `.replace(/^\s+|\n/gm, '');
    document.head.appendChild(styleTag);
}
