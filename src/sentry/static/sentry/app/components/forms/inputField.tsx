import PropTypes from 'prop-types';
import React from 'react';

import FormField from 'app/components/forms/formField';

type InputFieldProps = FormField['props'] & {
  placeholder: string;
  inputStyle?: object;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onKeyPress?: (event: React.KeyboardEvent<HTMLInputElement>) => void;
  onKeyDown?: (event: React.KeyboardEvent<HTMLInputElement>) => void;
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  autoComplete?: string;
};

export default class InputField<
  Props extends InputFieldProps = InputFieldProps,
  State extends FormField['state'] = FormField['state']
> extends FormField<Props, State> {
  static propTypes = {
    ...FormField.propTypes,
    placeholder: PropTypes.string,
  };

  getField() {
    return (
      <input
        {...this.props}
        id={this.getId()}
        type={this.getType()}
        className="form-control"
        onChange={this.onChange}
        value={this.state.value as string | number} //can't pass in boolean here
      />
    );
  }

  getClassName() {
    return 'control-group';
  }

  getType(): string {
    throw new Error('Must be implemented by child.');
  }
}
