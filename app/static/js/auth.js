(function() {
    'use strict';

    angular.module('SecureLoginApp', [])
        .controller('SecureLoginController', ['$scope', '$log', '$http', '$timeout',

            function($scope, $log, $http, $timeout) {

                $scope.displayLoginForm = function() {
                    $('#registration').toggleClass('hide-element', true);
                    $('#login').toggleClass('hide-element', false);
                }

                $scope.displayRegistrationForm = function() {
                    $('#login').toggleClass('hide-element', true);
                    $('#registration').toggleClass('hide-element', false);
                }

                $scope.userLogin = function() {
                    var email = $scope.loginEmail;
                    var password = $scope.loginPassword;
                    secureAuth(email, password, "login");
                }

                $scope.registerNewUser = function() {
                    var email = $scope.registerEmail;
                    var password = $scope.createPassword;
                    var confrimPassword = $scope.confirmPassword;
                    if (password == confrimPassword) {
                        $scope.registrationErrorMessage = null;
                        $('#registration-error').toggleClass('hide-element', false);
                        $('#registration-success').toggleClass('hide-element', true);

                        secureAuth(email, password, "register");
                    } else {
                        $scope.registrationErrorMessage = "Passwords do not match!";
                        $('#registration-error').toggleClass('hide-element', false);
                        $('#registration-success').toggleClass('hide-element', true);
                    }
                }

                function secureAuth(email, password, auth_type) {
                    generateSessionKey()
                        .then((key) => encryptUserCredentials(key, email, password))
                        .then(([key, iv, ct]) => encryptSessionKey(key, iv, ct))

                    .then(([enc_key, iv, ct]) => {
                            if (auth_type == "register") {
                                postRegistrationRequest(enc_key, iv, ct)
                            } else if (auth_type == "login") {
                                postLoginRequest(enc_key, iv, ct)
                            } else {
                                throw Error('Unkown auth type:' + auth_type);
                            }
                        })
                        .catch(function(err) {
                            alert("Error: " + err.message);
                        });
                }

                const generateSessionKey = function() {
                    var sessionKey = window.crypto.subtle.generateKey({
                            name: "AES-CBC",
                            length: 256
                        },
                        true, ["encrypt", "decrypt"]
                    );
                    return Promise.resolve(sessionKey);
                };

                const encryptUserCredentials = function(sessionKey, email, password) {
                    var ivBytes = window.crypto.getRandomValues(new Uint8Array(16));
                    var plainText = email + ":" + password;
                    var plainTextBytes = stringToByteArray(plainText);
                    var ivBase64 = byteArrayToBase64(ivBytes);

                    return window.crypto.subtle.encrypt({
                            name: "AES-CBC",
                            iv: ivBytes
                        },
                        sessionKey,
                        plainTextBytes
                    ).then(function(ciphertextBuffer) {
                        var cipherTextBytes = new Uint8Array(ciphertextBuffer);
                        var cipherTextBase64 = byteArrayToBase64(cipherTextBytes);

                        return [sessionKey, ivBase64, cipherTextBase64];
                    });
                };

                const encryptSessionKey = function(sessionKey, ivBase64, cipherTextBase64) {
                    var secureAuthDiv = document.getElementById('secure-auth');
                    var publicKeyHexString = secureAuthDiv.dataset.publicKey;
                    var publicKeyBytes = hexStringToByteArray(publicKeyHexString);

                    return window.crypto.subtle.importKey(
                        "spki",
                        publicKeyBytes, {
                            name: "RSA-OAEP",
                            hash: "SHA-256"
                        },
                        false, ["encrypt"]
                    ).then(function(publicKey) {
                        return window.crypto.subtle.exportKey(
                            "raw", sessionKey

                        ).then(function(sessionKeyBuffer) {

                            return window.crypto.subtle.encrypt({
                                    name: "RSA-OAEP"
                                },
                                publicKey,
                                sessionKeyBuffer
                            ).then(function(encryptedSessionKeyBuffer) {
                                var encryptedSessionKeyBytes = new Uint8Array(encryptedSessionKeyBuffer);
                                var encryptedSessionKeyBase64 = byteArrayToBase64(encryptedSessionKeyBytes);

                                return [encryptedSessionKeyBase64, ivBase64, cipherTextBase64];

                            }).catch(function(err) {
                                alert("Error occurred encrypting session key: " + err.message);
                            });

                        }).catch(function(err) {
                            alert("Error occurred exporting session key: " + err.message);
                        });

                    }).catch(function(err) {
                        alert("Error occurred importing public key: " + err.message);
                    });
                }

                const postRegistrationRequest = function(enc_key, iv, ct) {
                    $http.post(
                        "/api/v1/auth/register", {
                            'key': enc_key,
                            'iv': iv,
                            'ct': ct
                        }
                    ).then(successCallback, errorCallback);

                    function successCallback(response) {
                        $scope.authSuccessType = "SUCCESS";
                        $scope.authToken = response.data['Authorization'];
                        $('#auth-error').toggleClass('hide-element', true);
                        $('#auth-success').toggleClass('hide-element', false);
                        $('#auth-result-wrapper').toggleClass('hide-element', false);
                        return Promise.resolve();
                    }

                    function errorCallback(response) {
                        if (response.status == 401) {
                            $scope.authErrorType = "UNAUTHORIZED";
                        } else if (response.status == 409) {
                            $scope.authErrorType = "EMAIL ALREADY REGISTERED";
                        } else {
                            $scope.authErrorType = "SERVER ERROR";
                        }
                        $('#auth-success').toggleClass('hide-element', true);
                        $('#auth-error').toggleClass('hide-element', false);
                        $('#auth-result-wrapper').toggleClass('hide-element', false);
                        return Promise.reject(response.data);
                    }
                }

                const postLoginRequest = function(enc_key, iv, ct) {
                    $http.post(
                        "/api/v1/auth/login", {
                            'key': enc_key,
                            'iv': iv,
                            'ct': ct
                        }
                    ).then(successCallback, errorCallback);

                    function successCallback(response) {
                        $scope.authSuccessType = "SUCCESS";
                        $scope.authToken = response.data['Authorization'];
                        $('#auth-error').toggleClass('hide-element', true);
                        $('#auth-success').toggleClass('hide-element', false);
                        $('#auth-result-wrapper').toggleClass('hide-element', false);
                        return Promise.resolve();
                    }

                    function errorCallback(response) {
                        if (response.status == 401) {
                            $scope.authErrorType = "UNAUTHORIZED";
                        } else {
                            $scope.authErrorType = "SERVER ERROR";
                        }
                        $('#auth-success').toggleClass('hide-element', true);
                        $('#auth-error').toggleClass('hide-element', false);
                        $('#auth-result-wrapper').toggleClass('hide-element', false);
                        return Promise.reject(response.data);
                    }
                }

                function hexStringToByteArray(hexString) {
                    if (hexString.length % 2 !== 0) {
                        throw "Must have an even number of hex digits to convert to bytes";
                    }
                    var numBytes = hexString.length / 2;
                    var byteArray = new Uint8Array(numBytes);
                    for (var i = 0; i < numBytes; i++) {
                        byteArray[i] = parseInt(hexString.substr(i * 2, 2), 16);
                    }
                    return byteArray;
                }

                function stringToByteArray(s) {
                    var result = new Uint8Array(s.length);
                    for (var i = 0; i < s.length; i++) {
                        result[i] = s.charCodeAt(i);
                    }
                    return result;
                }

                function byteArrayToBase64(byteArray) {
                    var binaryString = "";
                    for (var i = 0; i < byteArray.byteLength; i++) {
                        binaryString += String.fromCharCode(byteArray[i]);
                    }
                    var base64String = window.btoa(binaryString);
                    return base64String;
                }
            }
        ]);
}());