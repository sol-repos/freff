import fs from 'fs';

const CLIENT_ID = "5472122f4b4b49bdb20d66adaa008f4c";
const CLIENT_SECRET = fs.readFileSync('/home/freff/server/secret.txt', 'utf8');

const APIController = (function() {
    const _getToken = async () => {
        const result = await fetch('https://accounts.spotify.com/api/token', {
            method: 'POST',
            headers: {
                'Content-Type' : 'application/x-www-form-urlencoded',
                'Authorization' : 'Basic' + btoa(CLIENT_ID + ':' + CLIENT_SECRET)
            },
            body: 'grant_type=client_credentials'
        });

        const data = await result.json();
        return data.access_token;
    }
})();