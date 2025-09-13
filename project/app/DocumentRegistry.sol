// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Document Registry
/// @notice Stores SHA-256 hashes of documents for authenticity verification
contract DocumentRegistry {
    // Mapping of document hash => stored flag
    mapping(bytes32 => bool) private documentHashes;

    // Event emitted whenever a hash is stored
    event DocumentStored(bytes32 indexed docHash, address indexed sender, uint256 timestamp);

    /// @notice Store a single document hash on-chain
    /// @param docHash SHA-256 hash of the document (bytes32)
    function storeHash(bytes32 docHash) external {
        require(!documentHashes[docHash], "Hash already exists");
        documentHashes[docHash] = true;
        emit DocumentStored(docHash, msg.sender, block.timestamp);
    }

    /// @notice Store multiple hashes in one transaction (batch insert)
    /// @param hashes Array of SHA-256 document hashes
    function storeHashes(bytes32[] calldata hashes) external {
        for (uint256 i = 0; i < hashes.length; i++) {
            if (!documentHashes[hashes[i]]) {
                documentHashes[hashes[i]] = true;
                emit DocumentStored(hashes[i], msg.sender, block.timestamp);
            }
        }
    }

    /// @notice Verify if a hash exists in the registry
    /// @param docHash SHA-256 hash of the document
    /// @return exists True if stored, false otherwise
    function verifyHash(bytes32 docHash) external view returns (bool exists) {
        return documentHashes[docHash];
    }
}
