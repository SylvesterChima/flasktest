var baseUri = "http://troologdemo.azurewebsites.net";
  const { createApp } = Vue
    createApp({
      data() {
        return {
          conversations: [],
          conversation: {},
          messages: [],
          newMessage: {
            recipient: "",
            type: "",
            conversationId: "",
            memberId: "",
            message: ""
          }
        }
      },
      delimiters: ['[[', ']]'],
      methods: {
        GetConversations(){
          this.conversations = [];
					const _this = this;
          axios.get(baseUri + '/conversations')
            .then(function (response) {
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
          this.messages = [];
          this.conversation = conv;
					const _this = this;
          mem = conv.members.filter(member => member.mobile_phone != "Business");
          axios.get(baseUri + '/messages/' + conv.id)
            .then(function (response) {
              _this.messages = response.data;
              _this.newMessage.recipient = mem.mobile_phone;
              _this.newMessage.memberId = mem.member_id;
              _this.newMessage.conversationId = conv.id;
              _this.newMessage.type = conv.type;
              _this.newMessage.message = "";
            })
            .catch(function (error) {
              // handle error
              console.log("*******22222****");
              console.log(error);
            })
            .finally(function () {
              // always executed
            });
        },
        SendMessage(newMessage){
          if(newMessage.message != ""){
            axios.post('/sendmessage', newMessage)
            .then(function (response) {
              console.log(response);
              this.messages.push(response.data)
            })
            .catch(function (error) {
              console.log(error);
            });
          }
        }
      },
      mounted() {
        this.GetConversations()
      }
    }).mount('#app')