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

function initialise(orgId) {
    createStyles();
    const container = document.createElement('div');
    container.style.position = 'fixed';
    Object.keys(position)
        .forEach(key => container.style[key] = position[key]);
    document.body.appendChild(container);

    const buttonContainer = document.createElement('div');
    buttonContainer.classList.add('button-container')

    const chatIcon = document.createElement('img');
    chatIcon.src = 'https://troologdemo.azurewebsites.net/static/uploads/chat.svg';
    chatIcon.classList.add('icon');
    this.chatIcon = chatIcon;

    const closeIcon = document.createElement('img');
    closeIcon.src = 'https://troologdemo.azurewebsites.net/static/uploads/cross.svg';
    closeIcon.classList.add('icon', 'hidden');
    this.closeIcon = closeIcon;

    buttonContainer.appendChild(this.chatIcon);
    buttonContainer.appendChild(this.closeIcon);

    const messageContainer = document.createElement('div');
    messageContainer.classList.add('hidden', 'message-container');
    messageContainer.classList.add('mchat');

    buttonContainer.addEventListener('click', function(){
        open = !open;
        if (open) {
            chatIcon.classList.add('hidden');
            closeIcon.classList.remove('hidden');
            messageContainer.classList.remove('hidden');
        } else {
            //createMessageContainerContent(messageContainer);
            chatIcon.classList.remove('hidden');
            closeIcon.classList.add('hidden');
            messageContainer.classList.add('hidden');
        }
    });

    this.createMessageIframe(messageContainer, orgId);
    //this.createMessageContainerContent(messageContainer);

    container.appendChild(messageContainer);
    container.appendChild(buttonContainer);
}

function createMessageIframe(messageContainer, orgId) {
    const iframe = document.createElement('iframe');
    iframe.src = 'https://troologdemo.azurewebsites.net/minichat/' + orgId
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
        }
        .icon {
            cursor: pointer;
            width: 70%;
            position: absolute;
            top: 9px;
            left: 9px;
            transition: transform .3s ease;
        }
        .hidden {
            transform: scale(0);
        }
        .button-container {
            background-color: #007bff;
            width: 60px;
            height: 60px;
            border-radius: 50%;
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
