var baseUri = "http://troologdemo.azurewebsites.net";
  const { createApp } = Vue
    createApp({
      data() {
        return {
          conversations: [],
          conversation: {},
          messages: [],
          recentMessages: [],
          newMessage: {
            recipient: "",
            type: "",
            conversationId: "",
            memberId: "",
            message: "",
            phoneId: "",
            pageId: ""
          }
        }
      },
      delimiters: ['[[', ']]'],
      methods: {
        GetConversations(){
          this.conversations = [];
					const _this = this;
          axios.get(baseUri + '/conversations/{{user.id}}')
            .then(function (response) {
              console.log(response);
              _this.conversations = response.data;
              if(_this.conversations.length > 0){
                _this.conversation = _this.conversations[0];
                _this.GetMessages(_this.conversation);
              }
            })
            .catch(function (error) {
              // handle error
              console.log(error);
            })
            .finally(function () {
              // always executed
            });
        },
        GetMessages(conv){
          console.log("***********");
          console.log(conv.members)
          this.messages = [];
          this.conversation = conv;
					const _this = this;
          if(conv.members.length > 0){
            mem = conv.members.filter(member => member.mobile_phone != "Business");
            console.log(mem)
            axios.get(baseUri + '/messages/' + conv.id)
              .then(function (response) {
                _this.messages = response.data;
                _this.newMessage.recipient = mem[0].mobile_phone;
                _this.newMessage.memberId = mem[0].id;
                _this.newMessage.conversationId = conv.id;
                _this.newMessage.type = conv.type;
                _this.newMessage.message = "";
                _this.newMessage.pageId = conv.page_id
              })
              .catch(function (error) {
                // handle error
                console.log("*******22222****");
                console.log(error);
              })
              .finally(function () {
                // always executed
              });
          }
        },
        GetRecentMessages(){
					const _this = this;
          axios.get(baseUri + '/recentmessages/' + _this.conversation.id)
            .then(function (response) {
              _this.recentMessages = response.data;
              _this.recentMessages.forEach(function (part, index){
                msg = _this.messages.filter(message => message.id == part.id);
                if(msg.length == 0){
                  _this.messages.push(part)
                }
              });
            })
            .catch(function (error) {
              console.log(error);
            })
            .finally(function () {
              // always executed
            });
        },
        SendMessage(newMessage){
          const _this = this;
          console.log(newMessage);
          if(newMessage.message != ""){
            console.log(newMessage);
            axios.post(baseUri + '/sendmessage', {
              type: newMessage.type,
              message: newMessage.message,
              recipient: newMessage.recipient,
              conversationId: newMessage.conversationId,
              memberId: newMessage.memberId
            })
            .then(function (response) {
              _this.newMessage.message = "";
              _this.messages.push(response.data)
            })
            .catch(function (error) {
              console.log(error);
            });
          }
        }
      },
      mounted() {
        this.GetConversations(),
        setInterval(this.GetRecentMessages, 4000)
      }
    }).mount('#app')