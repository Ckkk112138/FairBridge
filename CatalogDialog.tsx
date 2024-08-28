import { requestAPI, VRECell, CellPreview } from '@jupyter_vre/core';
import { Button, styled, TextField, ThemeProvider } from '@material-ui/core';
import { Autocomplete } from '@mui/material';
import * as React from 'react';
import { VirtualizedList, CellInfo } from '@jupyter_vre/components';
import { theme } from './Theme';

const catalogs = [

  { label: 'Local' }
];

interface IState {
  catalog_elements: [];
  current_cell: VRECell;
  current_cell_in_workspace: boolean;
  selectedFiles: File[];
}

export const DefaultState: IState = {
  catalog_elements: [],
  current_cell: null,
  current_cell_in_workspace: false,
  selectedFiles: []
};

const CatalogBody = styled('div')({
  display: 'flex',
  overflow: 'hidden',
  flexDirection: 'row'
});

const PreviewWindow = styled('div')({
  width: '400px',
  display: 'flex',
  flexDirection: 'column',
  overflowY: 'scroll'
});

const FileUploadArea = styled('div')(({ theme }) => ({
  margin: '15px',
  padding: '10px',
  border: `2px solid ${theme.palette.primary.main}`,
  borderRadius: '5px',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center'
}));

const FileList = styled('ul')({
  listStyle: 'none',
  padding: 0,
  margin: 0,
  width: '100%',
  maxHeight: '150px',
  overflowY: 'scroll'
});

const FileListItem = styled('li')({
  borderBottom: '1px solid #ccc',
  padding: '5px 0',
  textAlign: 'left'
});

interface CatalogDialogProps {
  addCellAction: (cell: VRECell) => void;
  isCellInWorkspace: (cell: VRECell) => boolean;
}

export class CatalogDialog extends React.Component<CatalogDialogProps> {

  state = DefaultState;
  cellPreviewRef: React.RefObject<CellPreview>;
  cellInfoRef: React.RefObject<CellInfo>;

  constructor(props: CatalogDialogProps) {
    super(props);
    this.cellPreviewRef = React.createRef();
    this.cellInfoRef = React.createRef();
  }

  componentDidMount(): void {
    this.getCatalog();
  }

  onCellSelection = (cell_index: number) => {

    let cell = this.state.catalog_elements[cell_index];
    let chart = cell['chart_obj'];
    let node = chart['nodes'][Object.keys(chart['nodes'])[0]];
    this.cellPreviewRef.current.updateChart(chart);
    this.cellInfoRef.current.updateCell(node, cell['types']);

    this.setState({
      current_cell: cell,
      current_cell_in_workspace: this.props.isCellInWorkspace(cell)
    });
  };

  onCellAddition = () => {

    this.props.addCellAction(this.state.current_cell);
    this.setState({ current_cell_in_workspace: true });
  };

  onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files ? Array.from(event.target.files) : [];
    this.setState((prevState: IState) => ({ // Explicitly type prevState as IState
      selectedFiles: prevState.selectedFiles.concat(files)
    }));
  };

  onDeleteFile = (index: number) => {
    this.setState((prevState :IState) => ({
      selectedFiles: prevState.selectedFiles.filter((_, i) => i !== index)
    }));
  };


  onCreateFDO = () => {
    if (!this.state.current_cell) {
      console.error('Current cell is null or undefined.');
      return;
    }

    const formData = new FormData();
    formData.append('cell', JSON.stringify(this.state.current_cell));
    if (this.state.selectedFiles.length > 0) {
      this.state.selectedFiles.forEach((file, index) => {
        formData.append(`file_${index}`, file);
      });
    }

    fetch('http://127.0.0.1:5000/upload', {  // Adjusted URL for localhost
      method: 'POST',
      body: formData
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to upload cell data.');
        }
        return response.json();
      })
      .then(responseData => {
        const redirectUrl = responseData.redirect_url;
        window.open(redirectUrl, '_blank');
        console.log('Enter FDO Creation');
      })
      .catch(error => {
        console.error('Error while uploading cell data:', error);
        // Handle error as needed
      });
  };


  getCatalog = async () => {

    const resp = await requestAPI<any>('catalog/cells/all', {
      method: 'GET'
    });

    this.setState({ catalog_elements: resp });
  };

  render(): React.ReactElement {
    return (
      <ThemeProvider theme={theme}>
        <p className="section-header">Explore Cell Catalogs</p>
        <CatalogBody>
          <div>
            <Autocomplete
              disablePortal
              id="combo-box-demo"
              options={catalogs}
              sx={{ width: 300, margin: '10px' }}
              renderInput={(params) => <TextField {...params} label="Catalog" />}
            />
            <VirtualizedList
              items={this.state.catalog_elements}
              clickAction={this.onCellSelection}
            />
          </div>
          <PreviewWindow>
            <div>
              <CellPreview ref={this.cellPreviewRef} />
              <CellInfo ref={this.cellInfoRef} />
              {this.state.current_cell != null ? (
                <div>
                  <Button color="primary"
                          disabled={this.state.current_cell_in_workspace}
                          style={{ margin: '15px' }}
                          variant="contained"
                          onClick={this.onCellAddition}>
                    Add to Workspace
                  </Button>
                  <FileUploadArea>
                      <input
                        type="file"
                        multiple
                        onChange={this.onFileChange}
                        style={{ marginBottom: '10px' }}
                      />
                      <FileList>
                        {this.state.selectedFiles.map((file, index) => (
                          <FileListItem key={index}>
                            {file.name}
                            <Button onClick={() => this.onDeleteFile(index)} color="primary" size="small">
                              Delete
                            </Button>
                          </FileListItem>
                        ))}
                      </FileList>
                    </FileUploadArea>
                  <Button color="primary"
                          style={{ margin: '15px' }}
                          variant="contained"
                          onClick={this.onCreateFDO}>
                    Create FDO
                  </Button>
                </div>
              ) : (<div></div>)}
            </div>
          </PreviewWindow>
        </CatalogBody>
      </ThemeProvider>
    );
  }
}