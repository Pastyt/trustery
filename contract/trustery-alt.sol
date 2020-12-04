//"SPDX-License-Identifier: UNLICENSED"

pragma solidity  ^0.7.2;

contract Trustery {
    struct Signature {
        address signer;
    }

    uint public attributes;
    Signature[1000] public signatures;
    uint public signcount;
    uint public revocations;

    event AttributeAdded(uint indexed attributeID, address indexed owner, string attributeType, bool has_proof, string indexed identifier, string data, string datahash);
    event AttributeSigned(uint indexed signatureID, address indexed signer, uint indexed attributeID, uint expiry);
    event SignatureRevoked(uint indexed revocationID, uint indexed signatureID);

    function addAttribute(string memory attributeType, bool has_proof, string memory identifier, string memory data, string memory datahash) public returns (uint attributeID) {

        attributeID = attributes++;
        
        emit AttributeAdded(attributeID, msg.sender, attributeType, has_proof, identifier, data, datahash);

    }

    function signAttribute(uint attributeID, uint expiry) public returns (uint signatureID) {

        signatureID=signcount++;
        signatures[signcount-1].signer=msg.sender;

        emit  AttributeSigned(signatureID, msg.sender, attributeID, expiry);

    }

    function revokeSignature(uint signatureID) public returns (uint revocationID) {

        require(signatures[signatureID].signer == msg.sender);
        revocationID = revocations++;

        emit SignatureRevoked(revocationID, signatureID);
        
    }
}