//"SPDX-License-Identifier: UNLICENSED"

pragma solidity  ^0.7.5;

contract Trustery {

    uint private attributes;
    address[] private signatures;
    uint private revocations;

    event AttributeAdded(uint indexed attributeID, address indexed owner, string attributeType, bool has_proof, bytes32 indexed identifier, string data, string datahash);
    event AttributeSigned(uint indexed signatureID, address indexed signer, uint indexed attributeID, uint expiry);
    event SignatureRevoked(uint indexed revocationID, uint indexed signatureID);

    function addAttribute(string memory attributeType, bool has_proof, bytes32 identifier, string memory data, string memory datahash) public returns (uint attributeID) {

        attributeID = attributes++;
        
        emit AttributeAdded(attributeID, msg.sender, attributeType, has_proof, identifier, data, datahash);
        return attributeID;

    }

    function signAttribute(uint attributeID, uint expiry) public returns (uint signatureID) {

        signatureID = signatures.length;
        signatures.push(msg.sender);
        emit  AttributeSigned(signatureID, msg.sender, attributeID, expiry);

    }

    function revokeSignature(uint signatureID) public returns (uint revocationID) {

        require(signatures[signatureID] == msg.sender);
        revocationID = revocations++;

        emit SignatureRevoked(revocationID, signatureID);
        
    }
}