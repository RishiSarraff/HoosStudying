import type { PipelineTagProps } from "../types"
import LabelImportantIcon from '@mui/icons-material/LabelImportant';

const PipelineTag: React.FC<PipelineTagProps> = ({pipeline_tag, index}) => {
    return(
        <div style={{ display: 'inline-flex', alignItems: 'center' }}>
            <LabelImportantIcon 
                sx={{ 
                    color: pipeline_tag.color,
                    fontSize: '1.2rem'
                }}
            />
            <span style={{ marginLeft: '4px', fontSize: '0.875rem' }}>
                {pipeline_tag.name}
            </span>
        </div>
    )
}

export default PipelineTag