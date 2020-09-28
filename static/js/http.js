class Fetch {
  constructor(method, url, json) {
    this.method = method;
    this.url = url;
    this.json = json;
  }

  fetch() {
    const response = fetch(this.url, {
      method: this.method,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(this.json)
    });
    return response;
  }
}

class HTTP {
  static get(url, json) {return new Fetch('GET', url, json).fetch();}
  static post(url, json) {return new Fetch('POST', url, json).fetch();}
  static put(url, json) {return new Fetch('PUT', url, json).fetch();}
  static delete(url, json) {return new Fetch('DELETE', url, json).fetch();}
}
