import React, { useState, useRef } from 'react';
import { Copy, RotateCcw, Edit, Save, History, Plus, Minus } from 'lucide-react';
import './StreamOutput.css';

interface StreamOutputProps {
  content: string;
  rawContent: string;
  isStreaming: boolean;
  onCopy?: () => void;
  onRegenerate?: () => void;
  onEdit?: (instruction: string, operation: 'expand' | 'compress' | 'polish' | 'edit') => void;
  documentId?: number;
  versions?: DocumentVersion[];
  currentVersion?: number;
}

interface DocumentVersion {
  id: number;
  version_number: number;
  formatted_content: string;
  version_note: string;
  operation_type: string;
  created_at: string;
}

const StreamOutput: React.FC<StreamOutputProps> = ({
  content,
  rawContent,
  isStreaming,
  onCopy,
  onRegenerate,
  onEdit,
  documentId,
  versions = [],
  currentVersion
}) => {
  const [showVersions, setShowVersions] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editInstruction, setEditInstruction] = useState('');
  const [editOperation, setEditOperation] = useState<'expand' | 'compress' | 'polish' | 'edit'>('edit');
  const [selectedVersion, setSelectedVersion] = useState(currentVersion);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      onCopy?.();
      // 可以添加复制成功的提示
    } catch (err) {
      console.error('复制失败:', err);
    }
  };

  const handleEdit = () => {
    if (editInstruction.trim() && onEdit) {
      onEdit(editInstruction, editOperation);
      setEditInstruction('');
      setEditMode(false);
    }
  };

  const handleVersionSelect = (version: DocumentVersion) => {
    setSelectedVersion(version.version_number);
    // 这里需要通过props传递给父组件来更新显示的内容
  };

  const displayContent = selectedVersion === currentVersion ? content : 
    versions.find(v => v.version_number === selectedVersion)?.formatted_content || content;

  return (
    <div className="stream-output">
      {/* 工具栏 */}
      <div className="output-toolbar">
        <div className="toolbar-left">
          <button 
            className="tool-btn" 
            onClick={handleCopy}
            title="复制内容"
          >
            <Copy size={16} />
            复制
          </button>
          
          <button 
            className="tool-btn" 
            onClick={onRegenerate}
            title="重新生成"
            disabled={isStreaming}
          >
            <RotateCcw size={16} />
            重新生成
          </button>
          
          <button 
            className="tool-btn" 
            onClick={() => setEditMode(!editMode)}
            title="编辑内容"
            disabled={isStreaming}
          >
            <Edit size={16} />
            编辑
          </button>
          
          {documentId && versions.length > 1 && (
            <button 
              className="tool-btn" 
              onClick={() => setShowVersions(!showVersions)}
              title="版本历史"
            >
              <History size={16} />
              版本 ({versions.length})
            </button>
          )}
        </div>
        
        <div className="toolbar-right">
          <span className="content-stats">
            {content.length} 字符
          </span>
        </div>
      </div>

      {/* 编辑面板 */}
      {editMode && (
        <div className="edit-panel">
          <div className="edit-operations">
            <label>
              <input 
                type="radio" 
                name="operation" 
                value="expand" 
                checked={editOperation === 'expand'}
                onChange={(e) => setEditOperation(e.target.value as any)}
              />
              <Plus size={16} /> 扩写
            </label>
            
            <label>
              <input 
                type="radio" 
                name="operation" 
                value="compress" 
                checked={editOperation === 'compress'}
                onChange={(e) => setEditOperation(e.target.value as any)}
              />
              <Minus size={16} /> 缩写
            </label>
            
            <label>
              <input 
                type="radio" 
                name="operation" 
                value="polish" 
                checked={editOperation === 'polish'}
                onChange={(e) => setEditOperation(e.target.value as any)}
              />
              <Edit size={16} /> 润色
            </label>
            
            <label>
              <input 
                type="radio" 
                name="operation" 
                value="edit" 
                checked={editOperation === 'edit'}
                onChange={(e) => setEditOperation(e.target.value as any)}
              />
              <Edit size={16} /> 自定义
            </label>
          </div>
          
          <div className="edit-input">
            <textarea
              value={editInstruction}
              onChange={(e) => setEditInstruction(e.target.value)}
              placeholder="请输入编辑要求，例如：增加更多细节、简化表达、优化语言等"
              rows={3}
            />
            
            <div className="edit-actions">
              <button 
                className="btn-primary"
                onClick={handleEdit}
                disabled={!editInstruction.trim()}
              >
                <Save size={16} />
                应用修改
              </button>
              
              <button 
                className="btn-secondary"
                onClick={() => {
                  setEditMode(false);
                  setEditInstruction('');
                }}
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 版本历史面板 */}
      {showVersions && (
        <div className="versions-panel">
          <h4>版本历史</h4>
          <div className="versions-list">
            {versions.map((version) => (
              <div 
                key={version.id}
                className={`version-item ${selectedVersion === version.version_number ? 'active' : ''}`}
                onClick={() => handleVersionSelect(version)}
              >
                <div className="version-header">
                  <span className="version-number">v{version.version_number}</span>
                  <span className="version-operation">{version.operation_type}</span>
                  <span className="version-date">
                    {new Date(version.created_at).toLocaleString()}
                  </span>
                </div>
                {version.version_note && (
                  <div className="version-note">{version.version_note}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 内容显示区域 */}
      <div 
        ref={contentRef}
        className={`output-content ${isStreaming ? 'streaming' : ''}`}
      >
        <div className="content-text">
          {displayContent.split('\n').map((line, index) => (
            <div key={index} className="content-line">
              {line || '\u00A0'} {/* 空行显示非断空格 */}
            </div>
          ))}
        </div>
        
        {isStreaming && (
          <div className="streaming-indicator">
            <span className="cursor">▊</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default StreamOutput;