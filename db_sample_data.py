#  insert into mstmenu
#  (menu_name,menu_icon,menu_path,parent_id, order_no)
#  values
#  ('Dashboard', 'LayoutDashboard', '/dashboard', NULL, 1),
#  ('Leads', 'Users', NULL, NULL, 2),
#  ('Buy Lead: Single', NULL, '/leads/buylead', 2, 3),
#  ('Buy Lead: List', NULL, '/leads/buyleadlist', 2, 4),
#  ('Untouched', NULL, '/leads/untouched', 2, 5),
#  ('Smart Assignment', 'Brain', NULL, NULL, 6),
#  ('Assignment Rules', NULL, '/assignment-rules', 6, 7),
#  ('Budget Segmentation', NULL, '/budget', 6, 8),
#  ('Make Expertise', NULL, '/expertise', 6, 9),
#  ('Workload Monitor', NULL, '/workload', 6, 10),
#  ('Round Robin Setup', NULL, '/round-robin', 6, 11),
#  ('SLA & Escalation', NULL, '/sla', 6, 12),
#  ('Automation', NULL, '/automation', 6, 13),
#  ('Buy', 'ShoppingCart', NULL, NULL, 14),
#  ('Tracker', NULL, '/leads/buyleadtracker', 14, 15),
#  ('Buy Lead: Bulk', NULL, '/leads/buyleadimport', 14, 16),
#  ('Untouched', NULL, '/leads/untouchedlist', 14, 17),
#  ('Lost/Re-Open', NULL, '/leads/buyleadlostlist', 14, 18),
#  ('Re-Allocation', NULL, '/leads/reallocationlist', 14, 19),
#  ('Followup', NULL, '/leads/buyleadfollowuplist', 14, 20),
#  ('Sale', 'TrendingUp', NULL, NULL, 21),
#  ('Untouched', NULL, '/leads/untouched', 21, 22);


#  insert into maprolemenu
#  (role_id, menu_id,created_by)
#  select 1, id, 1 from mstmenu;

#  insert into tblbank
#  (bank_name,created_by)
#  values
#  ('AXIS Bank','Harshang'),
#  ('ICICI Bank','Harshang');

#  insert into tblinsurance_company
#  (insurance_company_name,created_by)
#  values
#  ('National Insurance Co Ltd','Harshang'),
#  ('The Oriental Insurance Co Ltd','Harshang');


#  insert into mstmake
#  (make,is_premium,created_by)
#  values
#  ('Audi',true,'Harshang'),
#  ('Maruti',false,'Harshang');

#  insert into mstmodel
#  (make_id,model,created_by)
#  values
#  (1,'A3','Harshang'),
#  (1,'A4','Harshang'),
#  (2,'Waganor','Harshang'),
#  (2,'Alto','Harshang'),
#  (2,'XL6','Harshang');

#  insert into mstbranch
#  (branch,created_by)
#  values
#  ('YMCA','Harshang'),
#  ('Soliter Connect','Harshang');

#  insert into mstsource
#  (source,created_by)
#  values
#  ('Website','Harshang'),
#  ('Broker','Harshang');


#  insert into mstyear
#  (year)
#  values
#  (2026),
#  (2025);

#  insert into mstbroker
#  (broker,created_by)
#  values
#  ('ABC','Harshang'),
#  ('Test Test','Harshang');

#  insert into mststate
#  (state,created_by)
#  values
#  ('Gujarat','Harshang'),
#  ('Maharastra','Harshang');

#  insert into mstcity
#  (state_id,city,created_by)
#  values
#  (1,'Ahmedabad','Harshang'),
#  (1,'Surat','Harshang'),
#  (2,'Bombay','Harshang'),
#  (2,'Pune','Harshang');

#  INSERT INTO mstpart (part_name,created_by) VALUES ('Accident','Harshang');
#  INSERT INTO mstpart (part_name,created_by) VALUES ('Bumper','Harshang');
#  INSERT INTO mstpart (part_name,created_by) VALUES ('Bonet/Hood','Harshang');
