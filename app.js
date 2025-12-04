// Initialize Cytoscape
let cy = cytoscape({
    container: document.getElementById('cy'),
    
    elements: [
        // Nodes
        { data: { id: 'a', label: 'Node A' } },
        { data: { id: 'b', label: 'Node B' } },
        { data: { id: 'c', label: 'Node C' } },
        { data: { id: 'd', label: 'Node D' } },
        
        // Edges
        { data: { id: 'ab', source: 'a', target: 'b' } },
        { data: { id: 'bc', source: 'b', target: 'c' } },
        { data: { id: 'cd', source: 'c', target: 'd' } },
        { data: { id: 'da', source: 'd', target: 'a' } }
    ],
    
    style: [
        {
            selector: 'node',
            style: {
                'background-color': '#0074D9',
                'label': 'data(label)',
                'color': '#fff',
                'text-valign': 'center',
                'text-halign': 'center',
                'width': '60px',
                'height': '60px',
                'font-size': '14px'
            }
        },
        {
            selector: 'edge',
            style: {
                'width': 3,
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier'
            }
        },
        {
            selector: 'node:selected',
            style: {
                'background-color': '#FF4136',
                'border-width': 3,
                'border-color': '#333'
            }
        }
    ],
    
    layout: {
        name: 'circle'
    }
});

// Event listeners
cy.on('tap', 'node', function(evt) {
    const node = evt.target;
    console.log('Tapped on node: ' + node.id());
});

cy.on('tap', 'edge', function(evt) {
    const edge = evt.target;
    console.log('Tapped on edge: ' + edge.id());
});

// Helper functions
function resetGraph() {
    cy.layout({ name: 'circle' }).run();
}

let nodeCounter = 5;
function addNode() {
    const newId = String.fromCharCode(96 + nodeCounter);
    cy.add({
        data: { 
            id: newId, 
            label: 'Node ' + newId.toUpperCase() 
        }
    });
    nodeCounter++;
    resetGraph();
}
