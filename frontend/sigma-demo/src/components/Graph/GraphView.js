import { useState, useEffect } from 'react';
import { Sigma } from 'react-sigma';
import ForceAtlas2 from 'graphology-layout-forceatlas2';
import EdgeEditorModal from './EdgeEditorModal';
import { updateEdge } from '../../Services/api';

const GraphView = ({ graphData, setGraphData }) => {
  const [selectedEdge, setSelectedEdge] = useState(null);

  // 应用 ForceAtlas2 布局
  useEffect(() => {
    const layout = new ForceAtlas2();
    layout.assign(graphData);
  }, [graphData]);

  const handleEdgeClick = (event) => {
    setSelectedEdge(event.data.edge);
  };

  const handleUpdateWeight = async (newWeight) => {
    try {
      const updatedEdge = await updateEdge(selectedEdge.id, { weight: newWeight });
      setGraphData(prev => ({
        ...prev,
        edges: prev.edges.map(edge => 
          edge.id === selectedEdge.id ? updatedEdge : edge
        )
      }));
      setSelectedEdge(null);
    } catch (error) {
      alert('Failed to update edge');
    }
  };

  return (
    <div className="graph-container">
      <Sigma
        graph={graphData}
        settings={{ 
          drawEdges: true,
          defaultEdgeColor: '#666',
          edgeLabelSize: 'fixed'
        }}
        onClickEdge={handleEdgeClick}
      />

      {selectedEdge && (
        <EdgeEditorModal
          edge={selectedEdge}
          onClose={() => setSelectedEdge(null)}
          onSave={handleUpdateWeight}
        />
      )}
    </div>
  );
};

export default GraphView;