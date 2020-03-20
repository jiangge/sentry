import React from 'react';

import SettingsNavigation from 'app/views/settings/components/settingsNavigation';
import getConfiguration from 'app/views/settings/project/navigationConfiguration';
import withOrganization from 'app/utils/withOrganization';
import withProject from 'app/utils/withProject';
import {Organization, Project} from 'app/types';

type Props = {
  organization: Organization;
  project: Project;
};

const ProjectSettingsNavigation = ({organization, project}: Props) => {
  const features = new Set(organization.features);
  const navigationObjects = getConfiguration(project);
  console.log('navigationObjects', navigationObjects);
  return (
    <SettingsNavigation
      navigationObjects={navigationObjects}
      access={new Set(organization.access)}
      features={features}
      organization={organization}
      project={project}
    />
  );
};

export default withProject(withOrganization(ProjectSettingsNavigation));
