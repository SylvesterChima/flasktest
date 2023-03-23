const { createApp } = Vue
    createApp({
      data() {
        return {
          conversations: [],
          recipient: "hello"
          
        }
      },
      methods: {
        increment() {
          
        }
      },
      mounted() {
        console.log(`The initial count is ${this.count}.`)
      }
    }).mount('#app')